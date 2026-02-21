"""
Course Recommendation System
Integrates ML algorithms with Django
"""

try:
    import pandas as pd
    import numpy as np
    from sklearn.neighbors import NearestNeighbors
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    
from django.db.models import Avg, Count
from .models import Course, Enroll
from quizzes.models import Result
from django.contrib.auth.models import User


def get_user_course_matrix():
    """
    Create a user-course matrix based on enrollments and quiz scores
    Returns: DataFrame with users as rows, courses as columns, scores as values
    """
    if not PANDAS_AVAILABLE:
        return None
        
    # Get all enrollments
    enrollments = Enroll.objects.all()
    
    # Create matrix data
    matrix_data = []
    for enrollment in enrollments:
        user_id = enrollment.student.id
        course_id = enrollment.course.id
        
        # Get average quiz score for this user in this course
        from django.db.models import Avg as DjangoAvg
        results = Result.objects.filter(
            student=enrollment.student,
            quiz__info=enrollment.course
        )
        
        if results.exists():
            avg_score = results.aggregate(avg=DjangoAvg('marks'))['avg']
            score = avg_score if avg_score else 3.0  # Default to 3 if no quizzes
        else:
            score = 3.0  # Default enrollment score
        
        matrix_data.append({
            'user_id': user_id,
            'course_id': course_id,
            'score': score
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(matrix_data)
    
    if df.empty:
        return pd.DataFrame()
    
    # Pivot to create user-course matrix
    matrix = df.pivot_table(
        index='user_id',
        columns='course_id',
        values='score',
        fill_value=0
    )
    
    return matrix


def get_recommendations_knn(user, n_recommendations=5):
    """
    Get course recommendations using K-Nearest Neighbors algorithm
    
    Args:
        user: Django User object
        n_recommendations: Number of courses to recommend
    
    Returns:
        List of Course objects
    """
    # Get user-course matrix
    matrix = get_user_course_matrix()
    
    if matrix.empty or user.id not in matrix.index:
        # Return popular courses if no data
        return get_popular_courses(n_recommendations)
    
    # Get courses user hasn't enrolled in
    enrolled_courses = Enroll.objects.filter(student=user).values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_courses)
    
    if not available_courses.exists():
        return []
    
    # Train KNN model
    knn = NearestNeighbors(n_neighbors=min(5, len(matrix)), metric='cosine')
    knn.fit(matrix.values)
    
    # Get user's ratings vector
    user_vector = matrix.loc[user.id].values.reshape(1, -1)
    
    # Find similar users
    distances, indices = knn.kneighbors(user_vector)
    
    # Get courses liked by similar users
    similar_user_ids = matrix.index[indices[0][1:]]  # Exclude the user themselves
    
    recommendations = {}
    for similar_user_id in similar_user_ids:
        similar_user_courses = Enroll.objects.filter(
            student_id=similar_user_id
        ).exclude(
            course_id__in=enrolled_courses
        )
        
        for enrollment in similar_user_courses:
            course_id = enrollment.course.id
            if course_id not in recommendations:
                # Get score from matrix
                score = matrix.loc[similar_user_id, course_id] if course_id in matrix.columns else 3.0
                recommendations[course_id] = score
    
    # Sort by score and get top N
    sorted_courses = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    recommended_course_ids = [course_id for course_id, _ in sorted_courses[:n_recommendations]]
    
    return Course.objects.filter(id__in=recommended_course_ids)


def get_recommendations_correlation(user, n_recommendations=5):
    """
    Get course recommendations using correlation matrix
    
    Args:
        user: Django User object
        n_recommendations: Number of courses to recommend
    
    Returns:
        List of Course objects
    """
    # Get user-course matrix
    matrix = get_user_course_matrix()
    
    if matrix.empty:
        return get_popular_courses(n_recommendations)
    
    # Get courses user has enrolled in
    user_courses = Enroll.objects.filter(student=user)
    
    if not user_courses.exists():
        return get_popular_courses(n_recommendations)
    
    # Calculate correlation matrix
    course_correlation = matrix.T.corr()
    
    # Get recommendations based on user's enrolled courses
    recommendations = {}
    
    for enrollment in user_courses:
        course_id = enrollment.course.id
        
        if course_id not in course_correlation.columns:
            continue
        
        # Get similar courses
        similar_courses = course_correlation[course_id].sort_values(ascending=False)
        
        # Add to recommendations
        for similar_course_id, correlation in similar_courses.items():
            if similar_course_id != course_id and correlation > 0:
                if similar_course_id not in recommendations:
                    recommendations[similar_course_id] = 0
                recommendations[similar_course_id] += correlation
    
    # Exclude already enrolled courses
    enrolled_course_ids = user_courses.values_list('course_id', flat=True)
    recommendations = {
        course_id: score 
        for course_id, score in recommendations.items() 
        if course_id not in enrolled_course_ids
    }
    
    # Sort and get top N
    sorted_courses = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    recommended_course_ids = [course_id for course_id, _ in sorted_courses[:n_recommendations]]
    
    return Course.objects.filter(id__in=recommended_course_ids)


def get_popular_courses(n=5):
    """
    Get most popular courses (fallback when no personalized data available)
    
    Args:
        n: Number of courses to return
    
    Returns:
        QuerySet of Course objects
    """
    popular = Course.objects.annotate(
        enrollment_count=Count('enroll')
    ).order_by('-enrollment_count')[:n]
    
    return popular


def get_recommendations_for_user(user, method='knn', n=5):
    """
    Main function to get recommendations for a user
    
    Args:
        user: Django User object
        method: 'knn' or 'correlation'
        n: Number of recommendations
    
    Returns:
        List of Course objects with recommendation scores
    """
    if not PANDAS_AVAILABLE:
        # Fallback to popular courses if pandas not available
        return list(get_popular_courses(n))
        
    try:
        if method == 'knn':
            courses = get_recommendations_knn(user, n)
        elif method == 'correlation':
            courses = get_recommendations_correlation(user, n)
        else:
            courses = get_popular_courses(n)
        
        return list(courses)
    
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        # Fallback to popular courses
        return list(get_popular_courses(n))


def get_adaptive_quiz_difficulty(user, course):
    """
    Determine appropriate quiz difficulty based on user performance
    
    Args:
        user: Django User object
        course: Course object
    
    Returns:
        str: 'easy', 'medium', or 'hard'
    """
    # Get user's quiz results for this course
    results = Result.objects.filter(
        student=user,
        quiz__info=course
    )
    
    if not results.exists():
        return 'easy'  # Start with easy for new students
    
    # Calculate average performance
    from django.db.models import Avg
    avg_score = results.aggregate(Avg('marks'))['marks__avg']
    
    if avg_score is None:
        return 'easy'
    
    # Determine difficulty based on performance
    if avg_score < 60:
        return 'easy'
    elif avg_score < 80:
        return 'medium'
    else:
        return 'hard'


def get_weak_topics(user, course):
    """
    Identify topics where user needs improvement
    
    Args:
        user: Django User object
        course: Course object
    
    Returns:
        List of topic names where user scored below 70%
    """
    results = Result.objects.filter(
        student=user,
        quiz__info=course
    )
    
    weak_topics = []
    for result in results:
        if result.marks < 70:
            weak_topics.append(result.quiz.name)
    
    return weak_topics
