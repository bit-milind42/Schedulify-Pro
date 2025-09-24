/**
 * Professional Appointment Booking System
 * Enhanced JavaScript with modern interactions and animations
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    animationDelay: 100,
    toastDelay: 4000,
    transitionDuration: 300,
    fadeInDelay: 50
  };

  // DOM Helper Functions
  const DOM = {
    ready: callback => {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
      } else {
        callback();
      }
    },
    
    create: (tag, className, content) => {
      const element = document.createElement(tag);
      if (className) element.className = className;
      if (content) element.innerHTML = content;
      return element;
    },
    
    fadeIn: (element, delay = 0) => {
      setTimeout(() => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `all ${config.transitionDuration}ms ease-out`;
        
        requestAnimationFrame(() => {
          element.style.opacity = '1';
          element.style.transform = 'translateY(0)';
        });
      }, delay);
    },
    
    slideIn: (element, direction = 'left', delay = 0) => {
      setTimeout(() => {
        const transform = direction === 'left' ? 'translateX(-100%)' : 'translateX(100%)';
        element.style.transform = transform;
        element.style.transition = `transform ${config.transitionDuration}ms ease-out`;
        
        requestAnimationFrame(() => {
          element.style.transform = 'translateX(0)';
        });
      }, delay);
    }
  };

  // Animation Controller
  const Animations = {
    init: () => {
      // Animate cards on page load
      const cards = document.querySelectorAll('.card, .dashboard-card, .provider-card');
      cards.forEach((card, index) => {
        DOM.fadeIn(card, index * config.fadeInDelay);
      });

      // Animate form elements
      const formGroups = document.querySelectorAll('.form-group');
      formGroups.forEach((group, index) => {
        DOM.fadeIn(group, index * (config.fadeInDelay / 2));
      });

      // Animate table rows
      const tableRows = document.querySelectorAll('tbody tr');
      tableRows.forEach((row, index) => {
        DOM.fadeIn(row, index * 25);
      });
    },

    // Animate new elements when they're added to the DOM
    animateIn: (element, type = 'fade') => {
      if (type === 'fade') {
        DOM.fadeIn(element);
      } else if (type === 'slide') {
        DOM.slideIn(element);
      }
    }
  };

  // Enhanced Toast Notifications
  const Notifications = {
    init: () => {
      const jsonTag = document.getElementById('initial-messages');
      if (!jsonTag) return;
      
      let messages = [];
      try {
        messages = JSON.parse(jsonTag.textContent.trim());
      } catch(e) {
        console.warn('Failed to parse messages:', e);
        return;
      }
      
      const wrapper = Notifications.getOrCreateWrapper();
      
      messages.forEach((message, index) => {
        setTimeout(() => {
          Notifications.show(message.text, message.level, wrapper);
        }, index * 200);
      });
    },

    getOrCreateWrapper: () => {
      let wrapper = document.getElementById('toastWrapper');
      if (!wrapper) {
        wrapper = DOM.create('div', 'toast-container position-fixed top-0 end-0 p-3');
        wrapper.id = 'toastWrapper';
        wrapper.style.zIndex = '9999';
        document.body.appendChild(wrapper);
      }
      return wrapper;
    },

    show: (message, level = 'info', wrapper = null) => {
      if (!wrapper) wrapper = Notifications.getOrCreateWrapper();
      
      const typeClass = Notifications.getTypeClass(level);
      const icon = Notifications.getIcon(level);
      
      const toast = DOM.create('div', `toast align-items-center ${typeClass} border-0`);
      toast.role = 'alert';
      toast.ariaLive = 'assertive';
      toast.ariaAtomic = 'true';
      
      toast.innerHTML = `
        <div class="d-flex">
          <div class="toast-body d-flex align-items-center gap-2">
            <span class="toast-icon">${icon}</span>
            <span>${message}</span>
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                  data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      `;
      
      wrapper.appendChild(toast);
      
      // Animate in
      DOM.fadeIn(toast);
      
      // Initialize Bootstrap toast
      if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast, { delay: config.toastDelay });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
          toast.remove();
        });
      }
      
      return toast;
    },

    getTypeClass: (level) => {
      const levelMap = {
        'success': 'text-bg-success',
        'error': 'text-bg-danger',
        'warning': 'text-bg-warning',
        'info': 'text-bg-info'
      };
      
      // Handle Django message levels
      if (level.includes('success')) return levelMap.success;
      if (level.includes('error')) return levelMap.error;
      if (level.includes('warning')) return levelMap.warning;
      
      return levelMap.info;
    },

    getIcon: (level) => {
      const iconMap = {
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'info': 'ℹ'
      };
      
      if (level.includes('success')) return iconMap.success;
      if (level.includes('error')) return iconMap.error;
      if (level.includes('warning')) return iconMap.warning;
      
      return iconMap.info;
    }
  };

  // Time Slot Selection Enhancement
  const TimeSlots = {
    init: () => {
      const slots = document.querySelectorAll('.time-slot');
      
      slots.forEach(slot => {
        if (!slot.classList.contains('disabled')) {
          slot.addEventListener('click', TimeSlots.handleSelection);
          slot.addEventListener('mouseenter', TimeSlots.handleHover);
          slot.addEventListener('mouseleave', TimeSlots.handleLeave);
        }
      });
    },

    handleSelection: (event) => {
      const slot = event.currentTarget;
      
      // Remove previous selection
      const allSlots = document.querySelectorAll('.time-slot');
      allSlots.forEach(s => s.classList.remove('selected'));
      
      // Add selection to current slot
      slot.classList.add('selected');
      
      // Update hidden input if exists
      const hiddenInput = document.querySelector('input[name="time_slot"]');
      if (hiddenInput) {
        hiddenInput.value = slot.dataset.time || slot.textContent.trim();
      }
      
      // Animate selection
      slot.style.transform = 'scale(1.05)';
      setTimeout(() => {
        slot.style.transform = '';
      }, 150);
      
      // Enable next step if this is part of a multi-step process
      TimeSlots.enableNextStep();
    },

    handleHover: (event) => {
      const slot = event.currentTarget;
      if (!slot.classList.contains('disabled') && !slot.classList.contains('selected')) {
        slot.style.transform = 'translateY(-2px)';
      }
    },

    handleLeave: (event) => {
      const slot = event.currentTarget;
      if (!slot.classList.contains('selected')) {
        slot.style.transform = '';
      }
    },

    enableNextStep: () => {
      const nextButton = document.querySelector('.btn-next-step');
      if (nextButton) {
        nextButton.disabled = false;
        nextButton.classList.remove('btn-secondary');
        nextButton.classList.add('btn-primary');
      }
    }
  };

  // Form Enhancement
  const Forms = {
    init: () => {
      // Enhance all forms
      const forms = document.querySelectorAll('form');
      forms.forEach(Forms.enhanceForm);
      
      // Add floating labels
      Forms.initFloatingLabels();
      
      // Add form validation
      Forms.initValidation();
    },

    enhanceForm: (form) => {
      // Add loading state to submit buttons
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        form.addEventListener('submit', () => {
          Forms.setLoadingState(submitBtn);
        });
      }
      
      // Enhance file inputs
      const fileInputs = form.querySelectorAll('input[type="file"]');
      fileInputs.forEach(Forms.enhanceFileInput);
    },

    initFloatingLabels: () => {
      const inputs = document.querySelectorAll('.form-control');
      inputs.forEach(input => {
        if (input.value) {
          input.classList.add('has-value');
        }
        
        input.addEventListener('input', () => {
          if (input.value) {
            input.classList.add('has-value');
          } else {
            input.classList.remove('has-value');
          }
        });
      });
    },

    initValidation: () => {
      const forms = document.querySelectorAll('form[data-validate]');
      forms.forEach(form => {
        form.addEventListener('submit', Forms.validateForm);
      });
    },

    validateForm: (event) => {
      const form = event.currentTarget;
      let isValid = true;
      
      // Remove previous validation messages
      form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
      form.querySelectorAll('.form-control').forEach(el => {
        el.classList.remove('is-invalid', 'is-valid');
      });
      
      // Validate required fields
      const requiredFields = form.querySelectorAll('[required]');
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          Forms.showFieldError(field, 'This field is required');
          isValid = false;
        } else {
          field.classList.add('is-valid');
        }
      });
      
      // Validate email fields
      const emailFields = form.querySelectorAll('input[type="email"]');
      emailFields.forEach(field => {
        if (field.value && !Forms.isValidEmail(field.value)) {
          Forms.showFieldError(field, 'Please enter a valid email address');
          isValid = false;
        }
      });
      
      if (!isValid) {
        event.preventDefault();
        event.stopPropagation();
      }
    },

    showFieldError: (field, message) => {
      field.classList.add('is-invalid');
      
      const feedback = DOM.create('div', 'invalid-feedback', message);
      field.parentNode.appendChild(feedback);
    },

    isValidEmail: (email) => {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    setLoadingState: (button) => {
      const originalText = button.textContent;
      button.disabled = true;
      button.innerHTML = '<span class="spinner me-2"></span>Loading...';
      
      // Reset after form submission or timeout
      setTimeout(() => {
        button.disabled = false;
        button.textContent = originalText;
      }, 5000);
    },

    enhanceFileInput: (input) => {
      const wrapper = DOM.create('div', 'file-input-wrapper');
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);
      
      const label = DOM.create('label', 'file-input-label', 'Choose file...');
      wrapper.appendChild(label);
      
      input.addEventListener('change', () => {
        const fileName = input.files[0]?.name || 'Choose file...';
        label.textContent = fileName;
      });
    }
  };

  // Loading States
  const Loading = {
    show: (message = 'Loading...') => {
      const existing = document.getElementById('global-loading');
      if (existing) return;
      
      const overlay = DOM.create('div', 'loading-overlay');
      overlay.id = 'global-loading';
      overlay.innerHTML = `
        <div class="loading-content">
          <div class="spinner-large"></div>
          <p>${message}</p>
        </div>
      `;
      
      document.body.appendChild(overlay);
      DOM.fadeIn(overlay);
    },

    hide: () => {
      const overlay = document.getElementById('global-loading');
      if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), config.transitionDuration);
      }
    }
  };

  // Smooth Scrolling
  const Scroll = {
    init: () => {
      const links = document.querySelectorAll('a[href^="#"]');
      links.forEach(link => {
        link.addEventListener('click', Scroll.smoothScroll);
      });
    },

    smoothScroll: (event) => {
      event.preventDefault();
      const target = document.querySelector(event.currentTarget.getAttribute('href'));
      
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  };

  // Mobile Menu Enhancement
  const MobileMenu = {
    init: () => {
      const toggler = document.querySelector('.navbar-toggler');
      const navbar = document.querySelector('.navbar-collapse');
      
      if (toggler && navbar) {
        toggler.addEventListener('click', () => {
          navbar.classList.toggle('show');
        });
      }
    }
  };

  // Search Enhancement
  const Search = {
    init: () => {
      const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
      searchInputs.forEach(Search.enhanceSearchInput);
    },

    enhanceSearchInput: (input) => {
      let timeout;
      
      input.addEventListener('input', (event) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          Search.performSearch(event.target);
        }, 300);
      });
    },

    performSearch: (input) => {
      const query = input.value.toLowerCase();
      const searchTarget = input.dataset.searchTarget || '.searchable';
      const items = document.querySelectorAll(searchTarget);
      
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const match = text.includes(query);
        
        item.style.display = match || !query ? '' : 'none';
        
        if (match && query) {
          item.classList.add('search-highlight');
        } else {
          item.classList.remove('search-highlight');
        }
      });
    }
  };

  // Initialize everything when DOM is ready
  DOM.ready(() => {
    console.log('🚀 Appointment Booking System initialized');
    
    // Initialize all modules
    Notifications.init();
    Animations.init();
    TimeSlots.init();
    Forms.init();
    Scroll.init();
    MobileMenu.init();
    Search.init();
    
    // Add global CSS for loading and search
    const style = DOM.create('style');
    style.textContent = `
      .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity ${config.transitionDuration}ms ease-in-out;
      }
      
      .loading-content {
        text-align: center;
        color: white;
      }
      
      .spinner-large {
        width: 48px;
        height: 48px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top-color: #2563eb;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
      }
      
      .search-highlight {
        background: rgba(37, 99, 235, 0.1) !important;
      }
      
      .toast-icon {
        font-weight: bold;
        font-size: 1.1em;
      }
      
      .file-input-wrapper {
        position: relative;
        overflow: hidden;
      }
      
      .file-input-label {
        display: block;
        padding: 0.75rem;
        background: var(--gray-100);
        border: 1px solid var(--gray-300);
        border-radius: var(--radius-lg);
        cursor: pointer;
        transition: all 0.2s;
      }
      
      .file-input-label:hover {
        background: var(--gray-200);
      }
      
      .file-input-wrapper input[type="file"] {
        position: absolute;
        left: -9999px;
      }
    `;
    document.head.appendChild(style);
    
    // Global error handling
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
    });
    
    // Add loading state to all navigation
    const navLinks = document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        setTimeout(() => Loading.show(), 100);
      });
    });
    
    // Hide loading on page load
    window.addEventListener('load', () => {
      Loading.hide();
    });
  });

  // Expose utilities globally for other scripts
  window.AppBooking = {
    Notifications,
    Loading,
    DOM,
    Animations
  };

})();
