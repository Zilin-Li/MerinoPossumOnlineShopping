if (document.getElementById('subTotal')){
    var initialTotalPayment = parseFloat(document.getElementById('subTotal').textContent);
}
if (document.getElementById('gst')){
    var initialGst = parseFloat(document.getElementById('gst').textContent);

}

// Mapping of country values to shipping fees
var shippingRates = {
    "nz": 10.00,  // New Zealand
    "aus": 40.00,  // Australia
    "usa": 60.00, // USA 
    "can": 60.00 , // Canada
    "uk": 70.00, // UK 
    "eur": 70.00 // Europe
};
if (document.getElementById('country')){
    document.getElementById('country').addEventListener('change', updateShippingAndTotal)    
}

function updateShippingAndTotal() {
    var countryElement = document.getElementById('country');
    var selectedCountry = countryElement.value;
    var shippingFee = shippingRates[selectedCountry] || 0.00;  // Default to 0 if country not listed
    resetPaymentDetails();

    document.getElementById('shippingFee').textContent = shippingFee.toFixed(2);
    document.getElementById('totalPayment').textContent = (initialTotalPayment + shippingFee + initialGst).toFixed(2);   
}

function toggleDeliveryInfo(show) {
    var deliveryInfo = document.getElementById('deliveryInfo');
    var inputs = deliveryInfo.getElementsByTagName('input');
    var deliveryOptions = document.querySelectorAll('.delivery-options .form-label');

    resetPaymentDetails();

    if (initialTotalPayment >=200.00) {
        var shippingFee = 0.00;}
    else{
        var shippingFee = 10.00;
    }
    var pickupFee = 0.00;
   
    deliveryOptions.forEach(label => {
        label.classList.remove('selected');
    });

    if (show) {
        document.querySelector('label[for="delivery"]').classList.add('selected');
        deliveryInfo.style.display = 'block';
        Array.from(inputs).forEach(input => input.disabled = false);
        document.getElementById('totalPayment').textContent = (initialTotalPayment + shippingFee + initialGst).toFixed(2);
        document.getElementById('shippingFee').textContent = shippingFee.toFixed(2);
    } else {
        document.querySelector('label[for="pickup"]').classList.add('selected');
        deliveryInfo.style.display = 'none';
        Array.from(inputs).forEach(input => input.disabled = true);
        document.getElementById('totalPayment').textContent = (initialTotalPayment + pickupFee + initialGst).toFixed(2);
        document.getElementById('shippingFee').textContent = pickupFee.toFixed(2);
        document.getElementById('country').value = 'nz';
    }
}

// Reset Subtotal, GST, Shipping Fee and Total Payment
function resetPaymentDetails() {
    document.getElementById('subTotal').textContent = initialTotalPayment.toFixed(2);
    document.getElementById('gst').textContent = initialGst.toFixed(2);
    document.getElementById('shippingFee').textContent = '0.00';
    document.getElementById('totalPayment').textContent = initialTotalPayment.toFixed(2);
    // remove the oderDiscountContainer
    var oderDiscountContainer = document.getElementById('orderDiscount');
    oderDiscountContainer.style.display = 'none';
    // enable apply button
    if(document.getElementById('applyGiftCard')){document.getElementById('applyGiftCard').disabled = false};
    // reset the hidden fields
    if(document.getElementById('hiddenCardNumber')){document.getElementById('hiddenCardNumber').value=""}
}


document.addEventListener('DOMContentLoaded', function() {
    toggleDeliveryInfo(true); 
    
});


if (document.getElementById('applyGiftCard')) {
    document.getElementById('applyGiftCard').addEventListener('click', function() {
        var giftCardCode = document.getElementById('giftCardNumber').value;   
        // check if the gift card code is a 22-digit number and letters
        if (giftCardCode.match(/^[a-zA-Z0-9]{22}$/)) {
            fetch('/users/checkout/apply_gift_card', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ gift_card_code: giftCardCode })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.status === 'success') {
                    var totalPayment = parseFloat(document.getElementById('totalPayment').textContent);
                    var giftCardBalance = parseFloat(data.balance);  
                    // these variables are used to display the discount
                    var oderDiscountContainer = document.getElementById('orderDiscount'); 
                    var oderDiscount = document.getElementById('orderDiscountValue');
                    
                    // disable this button
                    document.getElementById('applyGiftCard').disabled = true;
                    
                    // these variables are used to update the hidden fields,use to pass the value to the server
                    // var hiddenDiscount = document.getElementById('hiddenDiscount');
                    // var hiddenTotal = document.getElementById('hiddenTotal');
                    var hiddenCardNumber = document.getElementById('hiddenCardNumber');
    
                    //if the gift card balance is greater than the total amount, the total amount will be 0               
                    if (giftCardBalance > totalPayment) {
                        newTotal = 0;
                        oderDiscount.textContent =totalPayment.toFixed(2);
    
                        // hiddenDiscount.value = totalPayment.toFixed(2);
                        // disable credit card payment
                        disableCreditCardPayment();
                    } else {
                        newTotal = (totalPayment - giftCardBalance).toFixed(2);
                        oderDiscount.textContent = giftCardBalance.toFixed(2);
                  
                        // hiddenDiscount.value = giftCardBalance.toFixed(2);
    
                        // enable credit card payment
                        enableCreditCardPayment();
                    }    
                    hiddenCardNumber.value = data.card_code;
                    // hiddenTotal.value = newTotal;
                    oderDiscountContainer.style.display = 'block';
                    document.getElementById('totalPayment').textContent = newTotal;
                } else {
                    alert('Failed to apply gift card: ' + data.message); 
                }
            })
            .catch(error => {
                console.error('Error applying gift card:', error); 
                alert('Error applying gift card: Please try again.'); 
            });
        } else {
            alert('Invalid gift card number. Please ensure it is a 22-digit number.'); 
        }
    });   
}


if (document.getElementById('paymentType')) {
document.getElementById('paymentType').addEventListener('change', function() {
    var paymentType = document.getElementById('paymentType').value; 
    var creditCardSection = document.getElementById('creditCardSection');
    // var paypalSection = document.getElementById('paypalSection');

    if (paymentType === 'creditCard') {
        enableCreditCardPayment();
        // creditCardSection.style.display = 'block'; 
        // paypalSection.style.display = 'none'; 
    } else if (paymentType === 'monthly') {
        disableCreditCardPayment();
        // creditCardSection.style.display = 'none'; 
        
    }
});}

// function disable credit card payment
function disableCreditCardPayment(){
    const creditCardName= document.getElementById('cardName');
    const creditCardNumber = document.getElementById('cardNumber');
    const expiryMonth = document.getElementById('cardMonth');
    const expiryYear = document.getElementById('cardYear');
    const cardCVC = document.getElementById('cardCVC');


    creditCardName.disabled = true;
    creditCardNumber.disabled = true;
    expiryMonth.disabled = true;
    expiryYear.disabled = true;
    cardCVC.disabled = true;
}
// function enable credit card payment
function enableCreditCardPayment(){
    const creditCardName= document.getElementById('cardName');
    const creditCardNumber = document.getElementById('cardNumber');
    const expiryMonth = document.getElementById('cardMonth');
    const expiryYear = document.getElementById('cardYear');
    const cardCVC = document.getElementById('cardCVC');

    creditCardName.disabled = false;
    creditCardNumber.disabled = false;
    expiryMonth.disabled = false;
    expiryYear.disabled = false;
    cardCVC.disabled = false;
}
