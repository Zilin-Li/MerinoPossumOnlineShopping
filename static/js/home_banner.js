// ******Banner slide functions*******
if(document.querySelector('.home-banner-container') !== null){
    

let slide =document.querySelectorAll('.home-banner-container .slide');
var current_slide = 0;
//Clear all slides 
function cls(){
    for(let i=0; i<slide.length; i++){
        slide[i].style.display = 'none';
    }
}
// Next slide
function banner_next(){
    stopAutoSlide()
    
    cls();
    if(current_slide === slide.length-1){
        current_slide = -1;
    } 
    current_slide ++;
    slide[current_slide].style.display = 'block';
    slide[current_slide].style.opacity = 0.4;

    var x =0.4;
    var intX = setInterval(()=>{
        x += 0.1;
        slide[current_slide].style.opacity = x;
        if(x >= 1){
            clearInterval(intX);
            x=0.4;
        }
    }, 100);
    autoSlide();
    }

// Previous slide
function banner_prev(){
    stopAutoSlide()
    cls();
    if(current_slide === 0){
        current_slide =slide.length;
    } 
    current_slide--;
    slide[current_slide].style.display = 'block';
    slide[current_slide].style.opacity = 0.4;
    var x =0.4;
    var intX = setInterval(()=>{
            x += 0.1;
            slide[current_slide].style.opacity = x;
            if(x >= 1){
                clearInterval(intX);
                x=0.4;
                autoSlide();
            }
        }, 100);
    }
// Auto start banner slide
function banner_auto_start(){
    cls();
    slide[current_slide].style.display = 'block';
    return autoSlide();

}
function stopAutoSlide() {
    clearInterval(autoSlideInterval);
}

function autoSlide() {
    autoSlideInterval = setInterval(banner_next, 3000); 
}

// Auto start banner slide
banner_auto_start();

}
