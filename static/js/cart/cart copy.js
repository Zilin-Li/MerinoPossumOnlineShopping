
    
    const quantityInput = document.getElementById('cart-quantity-input');
    const minusBtn = document.getElementById('minus-btn');
    const plusBtn = document.getElementById('plus-btn');

    
    if (quantityInput &&  minusBtn && plusBtn) {
      minusBtn.addEventListener('click', function() {
        console.log("minus button clicked");
          let currentValue = parseInt(quantityInput.value);
          let min = parseInt(quantityInput.min);
          if (currentValue > min) {
            quantityInput.value = currentValue - 1;
          }
        });
      
        plusBtn.addEventListener('click', function() {
          let currentValue = parseInt(quantityInput.value);
          let max = parseInt(quantityInput.max);
          if (currentValue < max +100) {
            quantityInput.value = currentValue + 1;
          }
        });
    
        quantityInput.addEventListener('change', function() {
          let currentValue = parseInt(quantityInput.value);
          let min = parseInt(quantityInput.min);
          let max = parseInt(quantityInput.max);
          if (currentValue < min) {
            quantityInput.value = min;
          } else if (currentValue > max) {
            quantityInput.value = max;
          }
        });
    
    }
  

