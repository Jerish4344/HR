// EMERGENCY FIX: Force correct step display for employee form
(function() {
    console.log("🛠️ Emergency step navigation fix loaded");
    
    function fixStepDisplay() {
        // 1. Determine current step 
        let currentStep = 1;
        
        // From URL
        if (window.location.pathname.includes('create/step2')) {
            currentStep = 2;
        } else if (window.location.pathname.includes('create/step3')) {
            currentStep = 3;
        } else if (window.location.pathname.includes('create/step4')) {
            currentStep = 4;
        }
        
        // From form input
        const stepInput = document.querySelector('input[name="step"]');
        if (stepInput && stepInput.value) {
            currentStep = parseInt(stepInput.value, 10);
        }
        
        console.log(`🔍 Detected current step: ${currentStep}`);
        
        // 2. FORCE display of correct step content with !important
        document.querySelectorAll('.form-step').forEach(step => {
            step.style.cssText = 'display: none !important';
        });
        
        const activeStep = document.getElementById(`step-${currentStep}-content`);
        if (activeStep) {
            activeStep.style.cssText = 'display: block !important';
            console.log(`✅ Activated step ${currentStep} content`);
        } else {
            console.error(`❌ Could not find content for step ${currentStep}`);
        }
        
        // 3. FORCE correct step indicator
        document.querySelectorAll('.step').forEach((indicator, index) => {
            // Step numbers are 1-indexed
            const stepNum = index + 1;
            
            if (stepNum === currentStep) {
                indicator.classList.add('active');
                indicator.classList.remove('completed');
            } else if (stepNum < currentStep) {
                indicator.classList.remove('active');
                indicator.classList.add('completed');
            } else {
                indicator.classList.remove('active');
                indicator.classList.remove('completed');
            }
        });
        
        // 4. Add emergency Continue button
        const form = document.querySelector('form');
        if (form && !document.querySelector('.emergency-button')) {
            const container = document.createElement('div');
            container.className = 'emergency-button';
            container.style.cssText = 'margin-top: 30px; padding: 20px; background: #f8f9fa; border-top: 1px solid #ddd; text-align: center;';
            
            const submitBtn = document.createElement('button');
            submitBtn.type = 'submit';
            submitBtn.className = 'btn btn-primary btn-lg';
            submitBtn.style.cssText = 'padding: 10px 30px; font-size: 18px;';
            
            if (currentStep < 4) {
                submitBtn.innerHTML = 'Continue to Next Step <i class="fas fa-arrow-right ms-2"></i>';
            } else {
                submitBtn.innerHTML = '<i class="fas fa-save me-2"></i> Create Employee';
                submitBtn.className = 'btn btn-success btn-lg';
            }
            
            container.appendChild(submitBtn);
            form.appendChild(container);
            console.log('➕ Added emergency continuation button');
        }
        
        // 5. Add debug info
        const debugInfo = document.createElement('div');
        debugInfo.innerHTML = `<strong>Debug:</strong> Current Step: ${currentStep}`;
        debugInfo.style.cssText = 'margin: 20px 0; padding: 10px; background: #f0f8ff; border: 1px solid #ccc; border-radius: 4px;';
        
        const cardBody = document.querySelector('.card-body');
        if (cardBody) {
            cardBody.insertBefore(debugInfo, cardBody.firstChild);
        }
    }
    
    // Apply fix immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixStepDisplay);
    } else {
        fixStepDisplay();
    }
    
    // Re-apply after a short delay (just in case)
    setTimeout(fixStepDisplay, 500);
    
    // Also re-apply on any click (defensive measure)
    document.addEventListener('click', function() {
        setTimeout(fixStepDisplay, 100);
    });
})();
