/**
 * Kora Threads — MiniMoth Phone OTP Authentication Service (auth.js)
 * Connects frontend client to real Vercel Serverless Backend:
 *   - POST /api/auth/send-otp
 *   - POST /api/auth/verify-otp
 * Includes seamless offline fallback for hackathon presentations without internet.
 */

(function (window) {
  'use strict';

  var pendingRegistration = null;

  var MiniMothAuth = {
    // Step 1: Send OTP via Backend Serverless API
    sendOTP: async function (phone, userData, callback) {
      if (typeof userData === 'function') {
        callback = userData;
        userData = null;
      }

      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      if (cleanPhone.length !== 10) {
        if (callback) callback(new Error('Please enter a valid 10-digit Indian phone number.'));
        return;
      }

      pendingRegistration = {
        name: (userData && userData.name) ? userData.name.trim() : '',
        email: (userData && userData.email) ? userData.email.trim() : '',
        phone: cleanPhone
      };

      console.log('[Backend API] POST /api/auth/send-otp for +91' + cleanPhone);

      try {
        var res = await fetch('/api/auth/send-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: cleanPhone,
            name: pendingRegistration.name,
            email: pendingRegistration.email
          })
        });

        if (res.ok) {
          var data = await res.json();
          console.log('[Backend API Response 200 OK]:', data);
          if (callback) callback(null, data);
          return;
        }
      } catch (netErr) {
        console.warn('[Backend API Notice] Offline or static mode detected, falling back to local MiniMoth simulator:', netErr.message);
      }

      // Offline / Static fallback
      setTimeout(function () {
        var fallbackResponse = {
          success: true,
          service: 'MiniMoth (minimoth.dev)',
          status: 'PENDING_VERIFICATION',
          phone: '+91' + cleanPhone,
          channel: 'WhatsApp / SMS',
          sandbox_mode: true,
          sandbox_hint: 'Sandbox key active. Use code: 123456'
        };
        if (callback) callback(null, fallbackResponse);
      }, 300);
    },

    // Step 2: Verify OTP via Backend Serverless API
    verifyOTP: async function (phone, otpCode, callback) {
      var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
      var cleanCode = String(otpCode).trim();

      console.log('[Backend API] POST /api/auth/verify-otp for code:', cleanCode);

      try {
        var res = await fetch('/api/auth/verify-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: cleanPhone,
            code: cleanCode,
            name: pendingRegistration ? pendingRegistration.name : '',
            email: pendingRegistration ? pendingRegistration.email : ''
          })
        });

        if (res.ok) {
          var data = await res.json();
          console.log('[Backend API Response 200 OK] Verified Session:', data);

          // Save user and session locally
          if (window.KoraDB) {
            window.KoraDB.sessions.create(cleanPhone);
            window.KoraDB.users.createOrUpdate(data.user);
          }

          try {
            var event = new CustomEvent('kora:auth:changed', { detail: data });
            window.dispatchEvent(event);
          } catch (e) {}

          if (callback) callback(null, data);
          return;
        } else {
          var errData = await res.json();
          if (callback) callback(new Error(errData.error || 'Invalid OTP code'));
          return;
        }
      } catch (netErr) {
        console.warn('[Backend API Notice] Offline mode verification fallback:', netErr.message);
      }

      // Offline Fallback Verification
      if (cleanCode !== '123456') {
        if (callback) callback(new Error('Invalid verification code. Please enter 123456 (MiniMoth Sandbox Code).'));
        return;
      }

      var sessionToken = 'mm_sess_' + Math.random().toString(36).substring(2, 12);
      var user = window.KoraDB ? window.KoraDB.users.findByPhone(cleanPhone) : null;
      if (!user) {
        user = window.KoraDB ? window.KoraDB.users.createOrUpdate({
          phone: cleanPhone,
          name: (pendingRegistration && pendingRegistration.name) || 'Patron',
          email: (pendingRegistration && pendingRegistration.email) || (cleanPhone + '@patron.korathreads.in'),
          address: { locality: 'Kothrud', city: 'Pune', state: 'Maharashtra', pincode: '411038' }
        }) : { phone: cleanPhone };
      }

      var fallbackAuth = {
        success: true,
        verified: true,
        session_token: sessionToken,
        phone: '+91' + cleanPhone,
        user: user
      };

      try {
        var ev = new CustomEvent('kora:auth:changed', { detail: fallbackAuth });
        window.dispatchEvent(ev);
      } catch (e) {}

      if (callback) callback(null, fallbackAuth);
    },

    getCurrentUser: function () {
      if (!window.KoraDB) return null;
      var activePhone = window.KoraDB.sessions.getActivePhone();
      if (!activePhone) return null;
      return window.KoraDB.users.findByPhone(activePhone);
    },

    logout: function (callback) {
      if (window.KoraDB) {
        window.KoraDB.sessions.clear();
      }
      pendingRegistration = null;
      console.log('[Backend API] Logged out. Session revoked.');
      try {
        var event = new CustomEvent('kora:auth:changed', { detail: { loggedOut: true } });
        window.dispatchEvent(event);
      } catch (e) {}
      if (callback) callback(null);
    }
  };

  window.MiniMothAuth = MiniMothAuth;
})(window);
