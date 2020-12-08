$('.creators-slide .owl-carousel').owlCarousel({
    loop:false,
    margin:20,
    nav:true,
    responsive:{
        0:{
            items:1
        },
        600:{
            items:2
        },
        768:{
            items:3
        },
        1000:{
            items:4
        },
        1280:{
            items:5
        }
    }
})

$('.featured-course-sec .owl-carousel').owlCarousel({
    loop:false,
    margin:0,
    nav:true,
    items:1
})

$('.stud-saying-slide .owl-carousel').owlCarousel({
    loop:false,
    margin:0,
    nav:true,
    items:1
})
$('.saying-slide .owl-carousel').owlCarousel({
    loop:false,
    margin:30,
    nav:true,
    responsive:{
        0:{
            items:1
        },
        768:{
            items:2
        },
        1000:{
            items:3
        }
    }
})

$(window).scroll(function () {
    if ($(window).scrollTop() > 150) {
      $('.header').addClass('sticky');
    } else {
      $('.header').removeClass('sticky');
    }
  });
