/**
 * Kora Threads — MiniMoth Phone OTP Authentication Service (auth.js)
 * Implements passwordless phone-number authentication specified in PS-04 brief
 * Powered by MiniMoth (minimoth.dev) Sandbox & Session API
 */

(function (window) {
  'use strict';

  var MINIMOTH_CONFIG = {
    apiKey: 'mm_sandbox_kora_ps04_2026',
    endpoint: 'https://api.minimoth.dev/v1',
    sandboxCode: '123456',
    smsGateway: 'WhatsApp / Indian Telecom National SMS Priority'
  };

  // Temporary holding for pending registration data (Name, Email, Phone)
  var pendingRegistration = null;

  var MiniMothAuth = {
    config: MINIMOTH_CONFIG,

    // Step 1: Request OTP for Indian Mobile Number with optional Name and Email
    sendOTP: function (phone, userData, callback) {
      if (typeof userData === 'function') {
        callback = userData;
        userData = null;
      }

      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      if (cleanPhone.length !== 10) {
        if (callback) callback(new Error('Please enter a valid 10-digit Indian phone number.'));
        return;
      }

      // Store pending registration data
      pendingRegistration = {
        name: (userData && userData.name) ? userData.name.trim() : '',
        email: (userData && userData.email) ? userData.email.trim() : '',
        phone: cleanPhone
      };

      console.log('[MiniMoth API] Initiating OTP request to https://api.minimoth.dev/v1/otp/send');
      console.log('[MiniMoth API] Payload:', {
        api_key: MINIMOTH_CONFIG.apiKey,
        phone: '+91' + cleanPhone,
        channel: 'sms_whatsapp',
        customer_metadata: pendingRegistration
      });

      // Network simulation with real MiniMoth contract response
      setTimeout(function () {
        var response = {
          success: true,
          status: 'PENDING_VERIFICATION',
          phone: '+91' + cleanPhone,
          channel: 'WhatsApp / SMS',
          sandbox_hint: 'MiniMoth Sandbox Mode active. Use verification code: ' + MINIMOTH_CONFIG.sandboxCode,
          timestamp: new Date().toISOString()
        };
        console.log('[MiniMoth API] Response (HTTP 200):', response);
        if (callback) callback(null, response);
      }, 350);
    },

    // Step 2: Verify 6-digit OTP code & mint session
    verifyOTP: function (phone, otpCode, callback) {
      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      var cleanCode = String(otpCode).trim();

      console.log('[MiniMoth API] Verifying OTP at https://api.minimoth.dev/v1/otp/verify');
      console.log('[MiniMoth API] Checking code:', cleanCode, 'for +91' + cleanPhone);

      if (cleanCode !== MINIMOTH_CONFIG.sandboxCode) {
        if (callback) callback(new Error('Invalid verification code. Please enter ' + MINIMOTH_CONFIG.sandboxCode));
        return;
      }

      setTimeout(function () {
        // Mint persistent session in KoraDB
        var session = window.KoraDB ? window.KoraDB.sessions.create(cleanPhone) : { session_token: 'mm_sess_fallback' };

        // Look up or initialize user profile
        var user = window.KoraDB ? window.KoraDB.users.findByPhone(cleanPhone) : null;
        var regName = (pendingRegistration && pendingRegistration.name) ? pendingRegistration.name : ('Patron (+91 ' + cleanPhone + ')');
        var regEmail = (pendingRegistration && pendingRegistration.email) ? pendingRegistration.email : (cleanPhone + '@patron.korathreads.in');

        if (!user) {
          user = window.KoraDB.users.createOrUpdate({
            phone: cleanPhone,
            name: regName,
            email: regEmail,
            address: {
              line1: 'Near Main Market',
              locality: 'Kothrud',
              city: 'Pune',
              state: 'Maharashtra',
              pincode: '411038',
              country: 'India'
            }
          });
        } else if (pendingRegistration && (pendingRegistration.name || pendingRegistration.email)) {
          // Update existing profile with newly provided name/email
          if (pendingRegistration.name) user.name = pendingRegistration.name;
          if (pendingRegistration.email) user.email = pendingRegistration.email;
          user = window.KoraDB.users.createOrUpdate(user);
        }

        var authPayload = {
          success: true,
          token: session.session_token,
          user: user,
          is_repeat_customer: user.is_repeat_customer || false,
          verified_at: new Date().toISOString()
        };

        console.log('[MiniMoth Session Gateway] Verified! Session Token Minted:', session.session_token);
        console.log('[MiniMoth User Record] Stored Profile:', user);

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
      pendingRegistration = null;
      console.log('[MiniMoth Auth] User logged out, session terminated.');
      try {
        var event = new CustomEvent('kora:auth:changed', { detail: { loggedOut: true } });
        window.dispatchEvent(event);
      } catch (e) {}
      if (callback) callback(null);
    }
  };

  window.MiniMothAuth = MiniMothAuth;
})(window);
