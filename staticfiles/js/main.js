/**
 * HR Management System - Main JavaScript
 * 
 * This file contains common JavaScript functions used throughout the HR Management System
 * including form validation, dynamic UI updates, and interactive elements.
 * 
 * Version: 1.0
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('HR Management System Initialized');
    
    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeFormValidation();
    setupNotifications();
    setupDynamicFormElements();
    initializeCharts();
    setupTableFilters();
    setupDatePickers();
    
    // Handle sidebar toggle on mobile
    const sidebarToggle = document.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Set up form validation for all forms with the 'needs-validation' class
 */
function initializeFormValidation() {
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find the first invalid field and focus it
                const invalidField = form.querySelector(':invalid');
                if (invalidField) {
                    invalidField.focus();
                }
                
                // Show custom error messages
                showValidationErrors(form);
            }
            
            form.classList.add('was-validated');
        }, false);
        
        // Real-time validation as user types
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    
                    // Clear any error message
                    const feedbackElement = this.nextElementSibling;
                    if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement.textContent = '';
                    }
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

/**
 * Display custom validation error messages
 * @param {HTMLFormElement} form - The form to show validation errors for
 */
function showValidationErrors(form) {
    // Find all invalid fields
    const invalidFields = form.querySelectorAll(':invalid');
    
    invalidFields.forEach(field => {
        let errorMessage = '';
        
        // Get the validation message based on the type of validation that failed
        if (field.validity.valueMissing) {
            errorMessage = field.getAttribute('data-required-message') || 'This field is required';
        } else if (field.validity.typeMismatch) {
            errorMessage = field.getAttribute('data-type-message') || 'Please enter a valid format';
        } else if (field.validity.patternMismatch) {
            errorMessage = field.getAttribute('data-pattern-message') || 'Please match the requested format';
        } else if (field.validity.tooShort) {
            errorMessage = field.getAttribute('data-minlength-message') || 
                `Please enter at least ${field.getAttribute('minlength')} characters`;
        } else if (field.validity.tooLong) {
            errorMessage = field.getAttribute('data-maxlength-message') || 
                `Please enter no more than ${field.getAttribute('maxlength')} characters`;
        } else if (field.validity.rangeUnderflow) {
            errorMessage = field.getAttribute('data-min-message') || 
                `Please enter a value greater than or equal to ${field.getAttribute('min')}`;
        } else if (field.validity.rangeOverflow) {
            errorMessage = field.getAttribute('data-max-message') || 
                `Please enter a value less than or equal to ${field.getAttribute('max')}`;
        } else if (field.validity.customError) {
            errorMessage = field.validationMessage;
        }
        
        // Display the error message
        let feedbackElement = field.nextElementSibling;
        if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement = document.createElement('div');
            feedbackElement.className = 'invalid-feedback';
            field.parentNode.insertBefore(feedbackElement, field.nextSibling);
        }
        
        feedbackElement.textContent = errorMessage;
    });
}

/**
 * Set up notification system
 */
function setupNotifications() {
    // Check for new notifications every 60 seconds
    setInterval(fetchNotifications, 60000);
    
    // Initial fetch
    fetchNotifications();
    
    // Setup notification click handlers
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.notification-item')) {
            const notificationItem = e.target.closest('.notification-item');
            const notificationId = notificationItem.getAttribute('data-notification-id');
            
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        }
    });
}

/**
 * Fetch notifications from the server
 */
function fetchNotifications() {
    // This would normally be an AJAX call to the server
    // For demonstration purposes, we'll simulate it
    
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        // Simulate getting a random number of notifications (0-5)
        const notificationCount = Math.floor(Math.random() * 6);
        
        // Update the badge
        notificationBadge.textContent = notificationCount;
        
        // Show/hide badge based on count
        if (notificationCount > 0) {
            notificationBadge.classList.remove('d-none');
        } else {
            notificationBadge.classList.add('d-none');
        }
    }
}

/**
 * Mark a notification as read
 * @param {string} notificationId - The ID of the notification to mark as read
 */
function markNotificationAsRead(notificationId) {
    console.log(`Marking notification ${notificationId} as read`);
    
    // This would normally be an AJAX call to the server
    // For demonstration purposes, we'll just log it
    
    // Remove the notification from the UI
    const notificationItem = document.querySelector(`.notification-item[data-notification-id="${notificationId}"]`);
    if (notificationItem) {
        notificationItem.classList.add('fade-out');
        
        // Remove after animation completes
        setTimeout(() => {
            notificationItem.remove();
            
            // Update the notification count
            const notificationBadge = document.querySelector('.notification-badge');
            if (notificationBadge) {
                const currentCount = parseInt(notificationBadge.textContent) || 0;
                if (currentCount > 0) {
                    notificationBadge.textContent = currentCount - 1;
                    
                    if (currentCount - 1 <= 0) {
                        notificationBadge.classList.add('d-none');
                    }
                }
            }
        }, 300);
    }
}

/**
 * Set up dynamic form elements
 */
function setupDynamicFormElements() {
    // Handle conditional form fields
    document.querySelectorAll('[data-toggle-field]').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const targetFieldId = this.getAttribute('data-toggle-field');
            const targetField = document.getElementById(targetFieldId);
            
            if (targetField) {
                if (this.checked) {
                    targetField.classList.remove('d-none');
                    
                    // If the field is required when shown
                    if (targetField.hasAttribute('data-required-when-shown')) {
                        targetField.setAttribute('required', '');
                    }
                } else {
                    targetField.classList.add('d-none');
                    
                    // Remove required attribute when hidden
                    if (targetField.hasAttribute('data-required-when-shown')) {
                        targetField.removeAttribute('required');
                    }
                }
            }
        });
        
        // Trigger change event to set initial state
        toggle.dispatchEvent(new Event('change'));
    });
    
    // Handle dynamic form fields (add/remove)
    document.querySelectorAll('.add-field-btn').forEach(button => {
        button.addEventListener('click', function() {
            const templateId = this.getAttribute('data-template');
            const containerSelector = this.getAttribute('data-container');
            
            const template = document.getElementById(templateId);
            const container = document.querySelector(containerSelector);
            
            if (template && container) {
                // Clone the template
                const newField = template.content.cloneNode(true);
                
                // Generate a unique ID for the new fields
                const timestamp = new Date().getTime();
                newField.querySelectorAll('[id]').forEach(el => {
                    const newId = `${el.id}_${timestamp}`;
                    el.id = newId;
                });
                
                // Add the new field to the container
                container.appendChild(newField);
                
                // Setup remove button
                const removeButton = container.querySelector('.remove-field-btn:last-child');
                if (removeButton) {
                    removeButton.addEventListener('click', function() {
                        const fieldGroup = this.closest('.field-group');
                        if (fieldGroup) {
                            fieldGroup.remove();
                        }
                    });
                }
            }
        });
    });
}

/**
 * Initialize charts on the dashboard
 */
function initializeCharts() {
    // This function is intentionally left minimal since chart initialization
    // is already handled in the specific template files using Chart.js
    
    // Responsive charts
    window.addEventListener('resize', function() {
        if (window.departmentChart) {
            window.departmentChart.resize();
        }
        if (window.attendanceChart) {
            window.attendanceChart.resize();
        }
        if (window.employmentTypeChart) {
            window.employmentTypeChart.resize();
        }
    });
}

/**
 * Set up table filters and sorting
 */
function setupTableFilters() {
    document.querySelectorAll('.filterable-table').forEach(table => {
        const tableId = table.id;
        
        // Setup search functionality
        const searchInput = document.querySelector(`#${tableId}-search`);
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
        
        // Setup column sorting
        table.querySelectorAll('th[data-sort]').forEach(header => {
            header.addEventListener('click', function() {
                const sortKey = this.getAttribute('data-sort');
                const sortDirection = this.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc';
                
                // Update sort direction
                this.setAttribute('data-sort-direction', sortDirection);
                
                // Remove sort indicators from all headers
                table.querySelectorAll('th[data-sort]').forEach(h => {
                    h.querySelector('.sort-indicator')?.remove();
                });
                
                // Add sort indicator to current header
                const indicator = document.createElement('span');
                indicator.className = 'sort-indicator ms-1';
                indicator.innerHTML = sortDirection === 'asc' ? '↑' : '↓';
                this.appendChild(indicator);
                
                // Sort the table
                sortTable(table, sortKey, sortDirection);
            });
        });
    });
}

/**
 * Sort a table by the specified column
 * @param {HTMLTableElement} table - The table to sort
 * @param {string} sortKey - The data attribute to sort by
 * @param {string} direction - The sort direction ('asc' or 'desc')
 */
function sortTable(table, sortKey, direction) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const dirModifier = direction === 'asc' ? 1 : -1;
    
    // Sort the rows
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.querySelector(`[data-sort-value="${sortKey}"]`)?.getAttribute('data-sort-value') || 
                      a.querySelector(`td:nth-child(${parseInt(sortKey) + 1})`)?.textContent.trim();
        
        const bValue = b.querySelector(`[data-sort-value="${sortKey}"]`)?.getAttribute('data-sort-value') || 
                      b.querySelector(`td:nth-child(${parseInt(sortKey) + 1})`)?.textContent.trim();
        
        // Check if values are dates
        const aDate = parseDate(aValue);
        const bDate = parseDate(bValue);
        
        if (aDate && bDate) {
            return (aDate - bDate) * dirModifier;
        }
        
        // Check if values are numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return (aNum - bNum) * dirModifier;
        }
        
        // Default to string comparison
        return aValue.localeCompare(bValue) * dirModifier;
    });
    
    // Remove all rows from the table
    rows.forEach(row => row.remove());
    
    // Add the sorted rows
    sortedRows.forEach(row => {
        table.querySelector('tbody').appendChild(row);
    });
}

/**
 * Parse a date string into a Date object
 * @param {string} dateString - The date string to parse
 * @returns {Date|null} - The parsed date or null if invalid
 */
function parseDate(dateString) {
    if (!dateString) return null;
    
    // Try different date formats
    const date = new Date(dateString);
    if (!isNaN(date)) {
        return date;
    }
    
    // Try DD/MM/YYYY format
    const parts = dateString.split(/[\/\-\.]/);
    if (parts.length === 3) {
        // Try both DD/MM/YYYY and MM/DD/YYYY
        const d1 = new Date(parts[2], parts[1] - 1, parts[0]);
        const d2 = new Date(parts[2], parts[0] - 1, parts[1]);
        
        if (!isNaN(d1)) return d1;
        if (!isNaN(d2)) return d2;
    }
    
    return null;
}

/**
 * Initialize date pickers on date input fields
 */
function setupDatePickers() {
    // This would normally use a date picker library
    // For simplicity, we'll just ensure date inputs have the right type
    
    document.querySelectorAll('input[data-type="date"]').forEach(input => {
        input.type = 'date';
        
        // Set max date to today for date of birth fields
        if (input.classList.contains('date-of-birth')) {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            input.setAttribute('max', `${year}-${month}-${day}`);
        }
    });
}

/**
 * Format a date for display
 * @param {Date|string} date - The date to format
 * @param {string} format - The format to use (default: 'MM/DD/YYYY')
 * @returns {string} - The formatted date
 */
function formatDate(date, format = 'MM/DD/YYYY') {
    if (!date) return '';
    
    const d = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(d)) return '';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    let formatted = format;
    formatted = formatted.replace('YYYY', year);
    formatted = formatted.replace('MM', month);
    formatted = formatted.replace('DD', day);
    
    return formatted;
}

/**
 * Handle multi-step forms
 */
document.addEventListener('DOMContentLoaded', function() {
    const multiStepForms = document.querySelectorAll('.multi-step-form');
    
    multiStepForms.forEach(form => {
        const steps = form.querySelectorAll('.form-step');
        const nextButtons = form.querySelectorAll('.next-step');
        const prevButtons = form.querySelectorAll('.prev-step');
        const stepIndicators = form.querySelectorAll('.step-indicator .step');
        
        // Initialize the form
        let currentStep = 0;
        showStep(currentStep);
        
        // Next button click handler
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Validate current step
                const currentStepElement = steps[currentStep];
                const inputs = currentStepElement.querySelectorAll('input, select, textarea');
                let isValid = true;
                
                inputs.forEach(input => {
                    if (input.hasAttribute('required') && !input.value) {
                        isValid = false;
                        input.classList.add('is-invalid');
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });
                
                if (isValid) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });
        
        // Previous button click handler
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                currentStep--;
                showStep(currentStep);
            });
        });
        
        // Show the specified step
        function showStep(stepIndex) {
            steps.forEach((step, index) => {
                if (index === stepIndex) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });
            
            // Update step indicators
            stepIndicators.forEach((indicator, index) => {
                if (index < stepIndex) {
                    indicator.classList.add('completed');
                    indicator.classList.remove('active');
                } else if (index === stepIndex) {
                    indicator.classList.add('active');
                    indicator.classList.remove('completed');
                } else {
                    indicator.classList.remove('active', 'completed');
                }
            });
            
            // Show/hide prev/next buttons
            form.querySelector('.prev-step')?.classList.toggle('d-none', stepIndex === 0);
            
            const isLastStep = stepIndex === steps.length - 1;
            form.querySelector('.next-step')?.classList.toggle('d-none', isLastStep);
            form.querySelector('[type="submit"]')?.classList.toggle('d-none', !isLastStep);
        }
    });
});

/**
 * Handle AJAX form submissions
 */
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading indicator
            const submitButton = form.querySelector('[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            
            // Collect form data
            const formData = new FormData(form);
            
            // Send AJAX request
            fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Handle success
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message || 'Operation completed successfully');
                    
                    // Redirect if specified
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                    
                    // Reset form if specified
                    if (data.resetForm) {
                        form.reset();
                    }
                } else {
                    // Show error message
                    showAlert('danger', data.message || 'An error occurred');
                    
                    // Show field errors
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) {
                                input.classList.add('is-invalid');
                                
                                // Add error message
                                let feedbackElement = input.nextElementSibling;
                                if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
                                    feedbackElement = document.createElement('div');
                                    feedbackElement.className = 'invalid-feedback';
                                    input.parentNode.insertBefore(feedbackElement, input.nextSibling);
                                }
                                
                                feedbackElement.textContent = data.errors[field];
                            }
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'An unexpected error occurred. Please try again.');
            })
            .finally(() => {
                // Restore submit button
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    });
});

/**
 * Show an alert message
 * @param {string} type - The alert type (success, danger, warning, info)
 * @param {string} message - The message to display
 * @param {number} duration - How long to show the alert in milliseconds (default: 5000)
 */
function showAlert(type, message, duration = 5000) {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to the page
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.appendChild(alertElement);
    } else {
        // Create container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        container.appendChild(alertElement);
        document.body.appendChild(container);
    }
    
    // Initialize the Bootstrap alert
    const bsAlert = new bootstrap.Alert(alertElement);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            bsAlert.close();
        }, duration);
    }
    
    // Remove from DOM after hidden
    alertElement.addEventListener('closed.bs.alert', function() {
        this.remove();
    });
}
