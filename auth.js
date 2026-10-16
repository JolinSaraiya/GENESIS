/**
 * Kora Threads — MiniMoth Phone OTP Authentication Service (auth.js)
 * Implements passwordless phone-number authentication specified in PS-04 brief
 * Powered by MiniMoth (minimoth.dev) Sandbox API
 */

(function (window) {
  'use strict';

  var MINIMOTH_CONFIG = {
    apiKey: 'mm_sandbox_kora_ps04_2026',
    endpoint: 'https://api.minimoth.dev/v1',
    sandboxCode: '123456',
    smsGateway: 'WhatsApp / Indian Telecom National SMS Priority'
  };

  var MiniMothAuth = {
    config: MINIMOTH_CONFIG,

    // Step 1: Request OTP for Indian Mobile Number
    sendOTP: function (phone, callback) {
      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      if (cleanPhone.length !== 10) {
        if (callback) callback(new Error('Please enter a valid 10-digit Indian phone number.'));
        return;
      }

      // Simulate network request to MiniMoth Sandbox API
      setTimeout(function () {
        var response = {
          success: true,
          status: 'PENDING_VERIFICATION',
          phone: '+91' + cleanPhone,
          channel: 'WhatsApp / SMS',
          sandbox_hint: 'Sandbox mode active. Use OTP: ' + MINIMOTH_CONFIG.sandboxCode,
          timestamp: new Date().toISOString()
        };
        console.log('[MiniMoth Auth] OTP dispatched:', response);
        if (callback) callback(null, response);
      }, 350);
    },

    // Step 2: Verify 6-digit OTP code & mint session
    verifyOTP: function (phone, otpCode, callback) {
      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      var cleanCode = String(otpCode).trim();

      if (cleanCode !== MINIMOTH_CONFIG.sandboxCode) {
        if (callback) callback(new Error('Invalid verification code. Please enter ' + MINIMOTH_CONFIG.sandboxCode));
        return;
      }

      setTimeout(function () {
        // Mint persistent session in KoraDB
        var session = window.KoraDB ? window.KoraDB.sessions.create(cleanPhone) : { token: 'mock_token' };

        // Look up or initialize user profile
        var user = window.KoraDB ? window.KoraDB.users.findByPhone(cleanPhone) : null;
        if (!user) {
          user = window.KoraDB.users.createOrUpdate({
            phone: cleanPhone,
            name: 'Customer (+91 ' + cleanPhone + ')',
            address: {
              line1: 'Near Main Market',
              locality: 'Shivajinagar',
              city: 'Pune',
              state: 'Maharashtra',
              pincode: '411005',
              country: 'India'
            }
          });
        }

        var authPayload = {
          success: true,
          token: session.session_token,
          user: user,
          is_repeat_customer: user.is_repeat_customer || false,
          verified_at: new Date().toISOString()
        };

        // Broadcast event for UI updates
        try {
          var event = new CustomEvent('kora:auth:changed', { detail: authPayload });
          window.dispatchEvent(event);
        } catch (e) {}

        if (callback) callback(null, authPayload);
      }, 400);
    },

    // Check if user has an active session
    getCurrentUser: function () {
      if (!window.KoraDB) return null;
      var activePhone = window.KoraDB.sessions.getActivePhone();
      if (!activePhone) return null;
      return window.KoraDB.users.findByPhone(activePhone);
    },

    // Invalidate session
    logout: function (callback) {
      if (window.KoraDB) {
        window.KoraDB.sessions.clear();
      }
      try {
        var event = new CustomEvent('kora:auth:changed', { detail: { loggedOut: true } });
        window.dispatchEvent(event);
      } catch (e) {}
      if (callback) callback(null);
    }
  };

  window.MiniMothAuth = MiniMothAuth;
})(window);
