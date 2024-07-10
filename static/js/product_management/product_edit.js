
function checkImage(url) {
    return /^(http|https):\/\/[^\s]+/.test(url) && /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(url);
}

if(document.getElementById('uploadButton')){document.getElementById('uploadButton').addEventListener('click', function() {
    var image_url = document.getElementById('image_url').value;
    if (image_url === '') {
        alert('Please input image url!');
        return;
    }
    if (!checkImage(image_url)) {
        alert('Image is not valid!');
        return;
    }
    document.getElementById('product-img-display').src = image_url;
    document.querySelector('.product-edit-main-image').style.removeProperty('display'); // Show the main image div
    document.querySelector('.product-edit-main-image-button').style.display = 'none'; // Hide the upload button div
    document.getElementById('uploadImageModal').style.display = 'none';
    document.querySelector('.modal-backdrop').remove();
    document.getElementById('main_image').value = image_url;
});}

if(document.getElementById('remove_image')){document.getElementById('remove_image').addEventListener('click', function() {
    document.getElementById('product-img-display').src = '';
    document.querySelector('.product-edit-main-image-button').style.removeProperty('display'); // Show the upload button div
    document.querySelector('.product-edit-main-image').style.display = 'none'; // Hide the main image div
    document.getElementById('main_image').value = '';
});}

