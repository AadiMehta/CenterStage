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

$('.close-btn').click( function() {
    $(".wrapper-main").toggleClass("sidebar-collapse");
} );

// Cache selectors
var lastId,
    topMenu = $("#top-menu"),
    topMenuHeight = topMenu.outerHeight()+15,
    // All list items
    menuItems = topMenu.find("a"),
    // Anchors corresponding to menu items
    scrollItems = menuItems.map(function(){
      var item = $($(this).attr("href"));
      if (item.length) { return item; }
    });

// Bind click handler to menu items
// so we can get a fancy scroll animation
menuItems.click(function(e){
  var href = $(this).attr("href"),
      offsetTop = href === "#" ? 0 : $(href).offset().top-topMenuHeight+1;
  $('html, body').stop().animate({ 
      scrollTop: offsetTop
  }, 1000);
  e.preventDefault();
});

// Bind to scroll
$(window).scroll(function(){
   // Get container scroll position
   var fromTop = $(this).scrollTop()+topMenuHeight;
   
   // Get id of current scroll item
   var cur = scrollItems.map(function(){
     if ($(this).offset().top < fromTop)
       return this;
   });
   // Get the id of the current element
   cur = cur[cur.length-1];
   var id = cur && cur.length ? cur[0].id : "";
   
   if (lastId !== id) {
       lastId = id;
       // Set/remove active class
       menuItems
         .parent().removeClass("active")
         .end().filter("[href='#"+id+"']").parent().addClass("active");
   }                   
});
