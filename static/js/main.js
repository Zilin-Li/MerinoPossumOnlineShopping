
function loadScript(url) {
  const script = document.createElement('script');
  script.src = url;
  document.head.appendChild(script);
}


// Load all scripts

loadScript('/static/js/home_banner.js');
loadScript('/static/js/product/prodect_detail.js');
loadScript('/static/js/product/gift_cards.js');
loadScript('/static/js/popular_report/popular_report.js');

loadScript('/static/js/cart/cart.js');
loadScript('/static/js/footer_info/clothing_size.js');
loadScript('/static/js/footer_info/delivery_info.js');
loadScript('/static/js/checkout/checkout.js');
loadScript('/static/js/product_management/product_edit.js');
loadScript('/static/js/product_management/product_list.js');



