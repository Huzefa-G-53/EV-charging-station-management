/**
 * EV Charging Station Management System
 * script.js — Global JS utilities
 */

'use strict';

// ── Delete Confirmation ───────────────────────────────────────────────────
function confirmDelete() {
  return window.confirm(
    'Are you sure you want to delete this record?\nThis action cannot be undone.'
  );
}

// ── Auto-dismiss Flash Alerts ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  // Auto-close success/info alerts after 4 seconds
  setTimeout(function () {
    document.querySelectorAll('.alert-success, .alert-info').forEach(function (el) {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    });
  }, 4000);

  // Uppercase vehicle number input as user types
  var vnInput = document.getElementById('vehicle_number');
  if (vnInput) {
    vnInput.addEventListener('input', function () {
      var pos = this.selectionStart;
      this.value = this.value.toUpperCase();
      this.setSelectionRange(pos, pos);
    });
  }

  // Highlight active nav link based on current path
  var path = window.location.pathname.split('/')[1];
  document.querySelectorAll('.navbar-nav .nav-link').forEach(function (link) {
    var href = link.getAttribute('href') || '';
    if (href.includes(path) && path !== '') {
      link.classList.add('active');
    }
  });
});
