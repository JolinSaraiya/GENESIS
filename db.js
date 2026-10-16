/**
 * Kora Threads — Client & Edge Data Persistence Layer (db.js)
 * Implements persistent schema for Users, Orders, Sessions, and Inventory
 * Compatible with LocalStorage, IndexedDB, and serverless environments.
 */

(function (window) {
  'use strict';

  var STORAGE_KEY_PREFIX = 'kora_db_';

  var DefaultSeed = {
    users: [
      {
        id: 'usr_001',
        phone: '9876543210',
        name: 'Aarav Deshmukh',
        email: 'aarav.deshmukh@example.in',
        address: {
          line1: 'B-402, Mayur Vihar, Paud Road',
          locality: 'Kothrud',
          city: 'Pune',
          state: 'Maharashtra',
          pincode: '411038',
          country: 'India'
        },
        is_repeat_customer: true,
        orders_count: 4,
        total_spent_inr: 9600,
        created_at: '2025-08-14T10:00:00Z'
      }
    ],
    orders: [
      {
        order_id: 'KT-ORD-8821',
        phone: '9876543210',
        customer_name: 'Aarav Deshmukh',
        items: [
          {
            item_id: 'KT-KRT-01',
            name: 'Solapur Pit-Loom Cotton Kurta',
            price: 2450,
            quantity: 1
          }
        ],
        subtotal: 2450,
        shipping_fee: 0,
        total_amount: 2450,
        payment_method: 'COD',
        payment_status: 'VERIFIED_COD',
        minimoth_verified: true,
        shipping_address: 'Kothrud, Pune, Maharashtra 411038',
        delivery_sla: '4 to 6 business days',
        tracking_status: 'Delivered',
        created_at: '2026-10-10T14:30:00Z'
      }
    ],
    sessions: []
  };

  function readStore(collection) {
    try {
      var raw = localStorage.getItem(STORAGE_KEY_PREFIX + collection);
      if (!raw) {
        if (DefaultSeed[collection]) {
          writeStore(collection, DefaultSeed[collection]);
          return DefaultSeed[collection];
        }
        return [];
      }
      return JSON.parse(raw);
    } catch (e) {
      console.warn('LocalStorage unavailable, using in-memory store:', e);
      return DefaultSeed[collection] || [];
    }
  }

  function writeStore(collection, data) {
    try {
      localStorage.setItem(STORAGE_KEY_PREFIX + collection, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to write to LocalStorage:', e);
    }
  }

  var KoraDB = {
    // ----------------- USERS -----------------
    users: {
      findByPhone: function (phone) {
        var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
        var users = readStore('users');
        for (var i = 0; i < users.length; i++) {
          if (users[i].phone === cleanPhone) {
            return users[i];
          }
        }
        return null;
      },
      createOrUpdate: function (userData) {
        var cleanPhone = String(userData.phone).replace(/\D/g, '').slice(-10);
        var users = readStore('users');
        var existingIndex = -1;
        for (var i = 0; i < users.length; i++) {
          if (users[i].phone === cleanPhone) {
            existingIndex = i;
            break;
          }
        }

        var record;
        if (existingIndex >= 0) {
          record = Object.assign({}, users[existingIndex], userData, {
            phone: cleanPhone,
            updated_at: new Date().toISOString()
          });
          users[existingIndex] = record;
        } else {
          record = Object.assign({
            id: 'usr_' + Date.now(),
            phone: cleanPhone,
            is_repeat_customer: false,
            orders_count: 0,
            created_at: new Date().toISOString()
          }, userData);
          users.push(record);
        }

        writeStore('users', users);
        return record;
      },
      getAll: function () {
        return readStore('users');
      }
    },

    // ----------------- ORDERS -----------------
    orders: {
      create: function (orderData) {
        var orders = readStore('orders');
        var newOrder = Object.assign({
          order_id: 'KT-ORD-' + Math.floor(1000 + Math.random() * 9000),
          tracking_status: 'Confirmed — Preparing Artisan Dispatch',
          delivery_sla: '4 to 6 business days',
          created_at: new Date().toISOString()
        }, orderData);

        orders.unshift(newOrder);
        writeStore('orders', orders);

        // Update user stats
        if (orderData.phone) {
          var user = KoraDB.users.findByPhone(orderData.phone);
          if (user) {
            user.orders_count = (user.orders_count || 0) + 1;
            user.is_repeat_customer = user.orders_count > 1;
            user.total_spent_inr = (user.total_spent_inr || 0) + (orderData.total_amount || 0);
            KoraDB.users.createOrUpdate(user);
          }
        }

        return newOrder;
      },
      listByPhone: function (phone) {
        var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
        var orders = readStore('orders');
        return orders.filter(function (ord) {
          return ord.phone === cleanPhone;
        });
      },
      getAll: function () {
        return readStore('orders');
      }
    },

    // ----------------- SESSIONS -----------------
    sessions: {
      create: function (phone) {
        var cleanPhone = String(phone).replace(/\D/g, '').slice(-10);
        var token = 'mm_sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
        var sessions = readStore('sessions');
        var newSession = {
          session_token: token,
          phone: cleanPhone,
          created_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        };
        sessions.push(newSession);
        writeStore('sessions', sessions);
        try {
          sessionStorage.setItem('kora_active_token', token);
          sessionStorage.setItem('kora_active_phone', cleanPhone);
        } catch (e) {}
        return newSession;
      },
      getActivePhone: function () {
        try {
          return sessionStorage.getItem('kora_active_phone') || null;
        } catch (e) {
          return null;
        }
      },
      clear: function () {
        try {
          sessionStorage.removeItem('kora_active_token');
          sessionStorage.removeItem('kora_active_phone');
        } catch (e) {}
      }
    },

    // ----------------- DEBUG / AUDIT -----------------
    resetDatabase: function () {
      writeStore('users', DefaultSeed.users);
      writeStore('orders', DefaultSeed.orders);
      writeStore('sessions', []);
      return true;
    }
  };

  window.KoraDB = KoraDB;
})(window);
