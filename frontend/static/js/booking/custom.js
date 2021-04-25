$('.sidebar-toggle').click( function() {
    $(".wrapper-main").toggleClass("sidebar-collapse");
} );

$('.close-btn').click( function() {
    $(".wrapper-main").toggleClass("sidebar-collapse");
} );

$('.videoButton').click( function() {
    $(".add-video-link").toggleClass("show");
} );


$('.video-slide .owl-carousel').owlCarousel({
    loop:true,
    margin:50,
    nav:true,
    responsive:{
        0:{
            items:1
        },

        1000:{
            items:2
        }
    }
})

$('.lessions-slide-wrap .owl-carousel').owlCarousel({
    loop:true,
    margin:20,
    nav:true,
    responsive:{
        0:{
            items:1
        },
        991:{
            items:2
        },
        1280:{
            items:3
        }
    }
})




