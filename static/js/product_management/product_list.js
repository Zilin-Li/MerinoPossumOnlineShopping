if(document.getElementById('variant_image_url')){
    document.getElementById('variant_image_url').addEventListener('change', function() {
    var imageUrl = this.value;
    var imagePreview = document.getElementById('variant_image_preview');
    if (imageUrl) {
        imagePreview.src = imageUrl;
        imagePreview.style.display = 'block';
    } else {
        imagePreview.src = '';
        imagePreview.style.display = 'none';
    }
});}

