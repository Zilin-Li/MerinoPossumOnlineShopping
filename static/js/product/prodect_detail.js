function selectProductColor(colorName,imageName,element) {

    document.getElementById('current-product-color').textContent = colorName;

    document.getElementById('product-img-display').src = 'https://raw.githubusercontent.com/LUMasterOfAppliedComputing2024S1/COMP639S1_Project_2_Group_AK_IMGS/main/'  + imageName;
    // document.getElementById('product-img-display').src = '/static/images/each_category/' + imageName;
     // Clear previous borders

     var images = document.querySelectorAll('#product-color-image img');

     images.forEach(function(img) {
         img.classList.remove('add-img-border'); 
     });

 
 
     // Add border to the clicked element's image
     element.querySelector('img').classList.add('add-img-border');
   
    
    }