function updateSubtotal(index) {
  const quantityInput = document.getElementById('quantity-' + index);
  const subtotalDisplay = document.getElementById('subtotal-' + index);
  const pricePerItem = parseFloat(quantityInput.dataset.price);
  let quantity = parseInt(quantityInput.value);

  if (isNaN(quantity) || quantity < parseInt(quantityInput.min)) {
    quantity = parseInt(quantityInput.min); 
    quantityInput.value = quantity;
  } else if (quantity > parseInt(quantityInput.max)) {
    quantity = parseInt(quantityInput.max);  
    quantityInput.value = quantity;
  }

  const newSubtotal = quantity * pricePerItem;
  subtotalDisplay.textContent = newSubtotal.toFixed(2);
}

function changeQuantity(isIncrement, index) {
  const quantityInput = document.getElementById('quantity-' + index);
  let currentValue = parseInt(quantityInput.value);
  const min = parseInt(quantityInput.min);
  const max = parseInt(quantityInput.max);

  if (isNaN(currentValue)) {
    currentValue = min;  
    quantityInput.value = currentValue;
  } else {
    if (isIncrement && currentValue < max) {
      quantityInput.value = currentValue + 1;
    } else if (!isIncrement && currentValue > min) {
      quantityInput.value = currentValue - 1;
    }
  }
  updateSubtotal(index);
}
