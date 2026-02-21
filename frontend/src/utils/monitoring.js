/**
 * Monitoring Utilities for Tracking User Engagement
 * Tracks tab switches, focus, time spent, etc.
 */

class MonitoringTracker {
  constructor() {
    this.sessionId = null;
    this.startTime = null;
    this.totalTime = 0;
    this.activeTime = 0;
    this.lastActiveTime = null;
    this.isActive = true;
    this.tabSwitches = 0;
    this.focusLostCount = 0;
    this.updateInterval = null;
    this.onEventCallback = null;
  }

  /**
   * Start monitoring session
   */
  start(sessionId, onEventCallback = null) {
    this.sessionId = sessionId;
    this.startTime = Date.now();
    this.lastActiveTime = Date.now();
    this.isActive = true;
    this.onEventCallback = onEventCallback;

    // Set up event listeners
    this.setupListeners();

    // Start time tracking interval
    this.updateInterval = setInterval(() => {
      this.updateTime();
    }, 1000); // Update every second

    console.log('Monitoring started:', sessionId);
  }

  /**
   * Stop monitoring session
   */
  stop() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    this.removeListeners();
    this.updateTime(); // Final update

    console.log('Monitoring stopped');
    console.log('Total time:', this.totalTime, 'seconds');
    console.log('Active time:', this.activeTime, 'seconds');
    console.log('Tab switches:', this.tabSwitches);
    console.log('Focus lost:', this.focusLostCount);
  }

  /**
   * Set up event listeners
   */
  setupListeners() {
    // Visibility change (tab switch)
    document.addEventListener('visibilitychange', this.handleVisibilityChange);

    // Window focus/blur
    window.addEventListener('focus', this.handleFocus);
    window.addEventListener('blur', this.handleBlur);

    // Mouse movement (activity detection)
    document.addEventListener('mousemove', this.handleActivity);
    document.addEventListener('keydown', this.handleActivity);
    document.addEventListener('click', this.handleActivity);
    document.addEventListener('scroll', this.handleActivity);
  }

  /**
   * Remove event listeners
   */
  removeListeners() {
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    window.removeEventListener('focus', this.handleFocus);
    window.removeEventListener('blur', this.handleBlur);
    document.removeEventListener('mousemove', this.handleActivity);
    document.removeEventListener('keydown', this.handleActivity);
    document.removeEventListener('click', this.handleActivity);
    document.removeEventListener('scroll', this.handleActivity);
  }

  /**
   * Handle visibility change (tab switch)
   */
  handleVisibilityChange = () => {
    if (document.hidden) {
      this.isActive = false;
      this.tabSwitches++;
      this.emitEvent('tab_switch', {
        hidden: true,
        timestamp: Date.now(),
      });
    } else {
      this.isActive = true;
      this.lastActiveTime = Date.now();
      this.emitEvent('tab_switch', {
        hidden: false,
        timestamp: Date.now(),
      });
    }
  };

  /**
   * Handle window focus
   */
  handleFocus = () => {
    this.isActive = true;
    this.lastActiveTime = Date.now();
    this.emitEvent('focus_gained', {
      timestamp: Date.now(),
    });
  };

  /**
   * Handle window blur
   */
  handleBlur = () => {
    this.isActive = false;
    this.focusLostCount++;
    this.emitEvent('focus_lost', {
      timestamp: Date.now(),
    });
  };

  /**
   * Handle user activity
   */
  handleActivity = () => {
    if (!this.isActive) {
      this.isActive = true;
      this.lastActiveTime = Date.now();
    }
  };

  /**
   * Update time tracking
   */
  updateTime() {
    const now = Date.now();
    const elapsed = Math.floor((now - this.startTime) / 1000);
    this.totalTime = elapsed;

    // Update active time if currently active
    if (this.isActive && this.lastActiveTime) {
      const activeElapsed = Math.floor((now - this.lastActiveTime) / 1000);
      if (activeElapsed < 5) {
        // Only count as active if less than 5 seconds since last activity
        this.activeTime++;
      }
    }

    // Emit time update event every 10 seconds
    if (this.totalTime % 10 === 0) {
      this.emitEvent('time_update', {
        total_time: this.totalTime,
        active_time: this.activeTime,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Emit event to callback — used ONLY for internal system events
   * (tab_switch, focus_lost, focus_gained, time_update).
   * Do NOT call this from trackEvent to avoid infinite recursion.
   */
  emitEvent(eventType, data) {
    if (this.onEventCallback && typeof this.onEventCallback === 'function') {
      this.onEventCallback(eventType, data);
    }
  }

  /**
   * Log a custom event — standalone, does NOT route through onEventCallback.
   * Safe to call from anywhere without risk of recursion.
   */
  logEvent(eventType, data) {
    // Log for debugging; can be extended to batch-send to backend
    console.debug('[MonitoringTracker] event:', eventType, data);
  }

  /**
   * Get current stats
   */
  getStats() {
    return {
      sessionId: this.sessionId,
      totalTime: this.totalTime,
      activeTime: this.activeTime,
      tabSwitches: this.tabSwitches,
      focusLostCount: this.focusLostCount,
      engagementRate: this.totalTime > 0 ? (this.activeTime / this.totalTime) * 100 : 0,
    };
  }

  /**
   * Reset tracker
   */
  reset() {
    this.sessionId = null;
    this.startTime = null;
    this.totalTime = 0;
    this.activeTime = 0;
    this.lastActiveTime = null;
    this.isActive = true;
    this.tabSwitches = 0;
    this.focusLostCount = 0;
  }
}

// Create singleton instance
const monitoringTracker = new MonitoringTracker();

export default monitoringTracker;

/**
 * Initialize monitoring for a session
 */
export function initializeMonitoring(sessionId, onEventCallback) {
  monitoringTracker.start(sessionId, onEventCallback);
  return monitoringTracker;
}

/**
 * Track a custom event.
 * This is a STANDALONE logger — it does NOT invoke the onEventCallback
 * registered via initializeMonitoring, so it is safe to call from anywhere
 * (including inside event handlers) without causing infinite recursion.
 */
export function trackEvent(eventType, data) {
  monitoringTracker.logEvent(eventType, data);
}

/**
 * Stop monitoring
 */
export function stopMonitoring() {
  monitoringTracker.stop();
}

/**
 * Get current monitoring stats
 */
export function getMonitoringStats() {
  return monitoringTracker.getStats();
}

/**
 * Format time in seconds to readable format
 */
export function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

/**
 * Calculate engagement score (0-100)
 */
export function calculateEngagementScore(stats) {
  const { totalTime, activeTime, tabSwitches, focusLostCount } = stats;

  if (totalTime === 0) return 0;

  // Base score from active time ratio
  const activeRatio = activeTime / totalTime;
  let score = activeRatio * 100;

  // Penalty for tab switches (max -20 points)
  const tabSwitchPenalty = Math.min(20, tabSwitches * 2);
  score -= tabSwitchPenalty;

  // Penalty for focus lost (max -10 points)
  const focusPenalty = Math.min(10, focusLostCount * 1);
  score -= focusPenalty;

  // Ensure score is between 0 and 100
  return Math.max(0, Math.min(100, Math.round(score)));
}
