$(document).ready(function() {
/***************************************/
/* This is for the formatting of the product prices */
/***************************************/
  var allPriceElem = document.getElementsByClassName("card__price")
  for (var i = 0; i < allPriceElem.length; i++) {
    allPrice = parseFloat(allPriceElem[i].textContent)
    formattedPrice = (allPrice).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    allPriceElem[i].innerHTML = '<span>&#8358;' + formattedPrice + '</span>'
  }

var confPrices = document.getElementsByClassName('cp')
for (var i = 0; i < confPrices.length; i++) {
  cPrice = parseFloat(confPrices[i].textContent)
  formated = (cPrice).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
  confPrices[i].innerHTML = '<span>&#8358;' + formated + '</span>'
}

 
/***************************************/
/* This is for the UI responsiveness  */
/***************************************/
function response() {
  let viewportWidth = window.innerWidth;

  container = document.getElementsByTagName('div')

  for (let i = 0; i < container.length; i++) {
    if (viewportWidth <= 650) {
      if (container[i].classList == "col-1-of-2") {
        container[i].classList.remove("col-1-of-2")
        container[i].classList.add("chima")
      } else if (container[i].classList == "col-1-of-4") {
        container[i].classList.remove("col-1-of-4")
        container[i].classList.add("chima1")
      }
    }

    if (viewportWidth > 650 ) {
      if (container[i].classList == "chima") {
        container[i].classList.remove("chima")
        container[i].classList.add("col-1-of-2")
      } else if (container[i].classList == "chima1") {
        container[i].classList.remove("chima1")
        container[i].classList.add("col-1-of-4")
      }
    }
  }
}

response()

$( window ).resize(response);

/***************************************/
/* This is for the cart functionality  */
/***************************************/  

  $("button#cart").click(function() {
      var id = $(this).find("#cartId").val()
      var check = $(this).hasClass('card__btn')
      if (check) {
        $(this).removeClass('card__btn')
        $(this).addClass('card__added')
        $(this).text('added')
      } else {
        $(this).text('added')
      }
  
      var csrf = "{{ csrf_token() }}" 

      //Make Ajax request
      var tosend = {"id":id, "csrf_token":csrf}
      $.ajax({
          url:"/cart/add",
          type: 'get',
          data: tosend,
          success: function(server_rsp) {
            window.sessionStorage.setItem('cartitems', server_rsp);
            console.log(server_rsp)
            $("span#c").text(server_rsp.toString())
          },
          error: function(err) {
              console.log(err)
          },        
      }) 
  });
 
  $("button#delcart").click(function() {
    $(this).parent().parent().remove()
    var id = $(this).find("#prodId").val()
    var item = $(this).parent().siblings('td.price').html()
    var remTotal = $(".total").text()
    var newTotal = remTotal - item
    $(".total").text(newTotal)
    var csrf = "{{ csrf_token() }}"

    //Make Ajax request
    var tosend = {"id":id, "csrf_token":csrf}
    $.ajax({
        url:"/cart/remove",
        type: 'get',
        data: tosend,
        success: function(server_rsp) {
          window.localStorage.setItem('cartitems', server_rsp);
          $("span#c").text(server_rsp)
        },
        error: function(err) {
            console.log(err)
        },        
    }) 
   
  })
  
  var initTotal = 0
  function tot(elem) {
    for (var i = 0; i < elem.length; i++) {
      initTotal = initTotal + parseInt(elem[i].textContent)
    }
    formattedInitTot = (initTotal).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
    iTotal = formattedInitTot
  }
  
  var allInitElem = document.getElementsByClassName("price")
  tot(allInitElem)
 
  $(".total").text(initTotal)


  $("select#qty").click(function() {
    $(this).change(function() {
      var x = $(this).val()
      var y = $(this).siblings("input#cprice").val();
      var newPrice = y * x
      $(this).parent().siblings("td.price").html(newPrice)
    })
    var total = 0
    var allElem = document.getElementsByClassName("price")
    for (var i = 0; i < allElem.length; i++) {
       total = total + parseInt(allElem[i].textContent)
    }  
    $(".total").text(total)
  }) 

  $("#hirebox").hide()
  $('#hire').click(function(){

      var user = $('#hire').prop('checked')
      if (user) {
          $("#hirebox").show()
          $("#price").hide()
      } else {
          $("#hirebox").hide()
      }
  })
 
  $('#sale').click(function(){
      $("#hirebox").hide()
  })

  /********************************/
  /* User Registration Validation */
  /********************************/
  $("#username").change(function() {
    var username = $('#username').val()
    data2send = "username="+username

    $.ajax({
        url:"/check/username",
        type: "get",
        data: data2send,
        success: function(msg) {
            if (msg=="Username is taken") {
                $("#alert").html(msg)
                $('#btnsubmit').attr('disabled','disabled')
                $('#btnsubmit').css('opacity','0.7')
            } else{
                $("#alert").css('color','green')
                $("#alert").html(msg)
                $("#btnsubmit").removeAttr('disabled')
                $('#btnsubmit').css('opacity','1')
            }
        },
        error: function(err) {}
    })
  })

  

});

