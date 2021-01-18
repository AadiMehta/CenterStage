// ****** Event Handlers ****** 

function handleLCS2Proceed() {
  let isValid = true;
  $('#startDatePickerError').hide();
  $('#endDatePickerError').hide();
  $('#MonStartTimeError').hide();
  $('#MonEndTimeError').hide();
  $('#TueStartTimeError').hide();
  $('#TueEndTimeError').hide();
  $('#WedStartTimeError').hide();
  $('#WedEndTimeError').hide();
  $('#ThuStartTimeError').hide();
  $('#ThuEndTimeError').hide();
  $('#FriStartTimeError').hide();
  $('#FriEndTimeError').hide();
  $('#SatStartTimeError').hide();
  $('#SatEndTimeError').hide();
  $('#SunStartTimeError').hide();
  $('#SunEndTimeError').hide();
  $('#timezoneSelectError').hide();
  $('#pricePerSessionValueError').hide();
  $('#weeklyPriceValueError').hide();
  $('#monthlyPriceValueError').hide();
  const startDate = $('#startDatepicker')[0].value;
  const endDate = $('#endDatepicker')[0].value;
  const timezone = $('#timezoneSelect')[0].value;
  const pricePerSessionCheck = $('#pricePerSessionCheck')[0].checked
  const pricePerSessionCurrency = $('#pricePerSessionCurrency')[0].value
  const pricePerSessionValue = $('#pricePerSessionValue')[0].value
  const weeklyPriceCheck = $('#weeklyPriceCheck')[0].checked
  const weeklyPriceCurrency = $('#weeklyPriceCurrency')[0].value
  const weeklyPriceValue = $('#weeklyPriceValue')[0].value
  const monthlyPriceCheck = $('#monthlyPriceCheck')[0].checked
  const monthlyPriceCurrency = $('#monthlyPriceCurrency')[0].value
  const monthlyPriceValue = $('#monthlyPriceValue')[0].value
  const $weekdaysInput = $('#weekdaysInput');
  let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];

  console.log(timezone)

  weekDayList.map((day) => {
    console.log(day)
    if (!$(`#${day}StartTime`)[0].value) {
      $(`#${day}StartTimeError`).text('Please Provide Start Time');
      $(`#${day}StartTimeError`).show()
      isValid = false;      
    }
    if (!$(`#${day}EndTime`)[0].value) {
      $(`#${day}EndTimeError`).text('Please Provide End Time');
      $(`#${day}EndTimeError`).show()
      isValid = false;      
    }
  })
  if (!startDate) {
    $('#startDatePickerError').text('Please Select Start Date');
    $('#startDatePickerError').show()
    isValid = false;
  }
  if (!endDate) {
    $('#endDatePickerError').text('Please Select End Date');
    $('#endDatePickerError').show()
    isValid = false;
  }
  if (timezone === 'none') {
    $('#timezoneSelectError').text('Please Select Timezone');
    $('#timezoneSelectError').show()
    isValid = false;
  }
  if (pricePerSessionCheck && (!pricePerSessionCurrency || !pricePerSessionValue)) {
    $('#pricePerSessionValueError').text('Please Provide Price Per Session Currency and Price');
    $('#pricePerSessionValueError').show()
    isValid = false;  
  }
  if (weeklyPriceCheck && (!weeklyPriceCurrency || !weeklyPriceValue)) {
    $('#weeklyPriceValueError').text('Please Provide Weekly Session Currency and Price');
    $('#weeklyPriceValueError').show()
    isValid = false;  
  }
  if (monthlyPriceCheck && (!monthlyPriceCurrency || !monthlyPriceValue)) {
    $('#monthlyPriceValueError').text('Please Provide Monthly Session Currency and Price');
    $('#monthlyPriceValueError').show()
    isValid = false;  
  }
  if (isValid) {
    $("#step2").submit();
  }
}

function calculateNumberOfSessions() {
  const startDate = $('#startDatepicker')[0].value;
  const endDate = $('#endDatepicker')[0].value;
  const $weekdaysInput = $('#weekdaysInput');
  let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];

  const startDateObj = dateFns.parse(startDate, 'MM/dd/yyyy', new Date());
  const endDateObj = dateFns.parse(endDate, 'MM/dd/yyyy', new Date());
  const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  var result = dateFns.eachDay(
    startDateObj,
    endDateObj
  )
  let noOfSessions = 0;
  result.map((item) => {
    const weekDay = weekdays[item.getDay()]
    if (weekDayList.includes(weekDay)) {
      noOfSessions += 1;
    }
  })
  $('#noOfSessions')[0].value = noOfSessions;
}

function handleSesionDaysSelect(event) {
  const $eventTarget = $(event.target);
  const $weekdaysInput = $('#weekdaysInput');
  let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];
  const targettedWeekday = event.currentTarget.dataset.weekday;
  const $dayStartTime = $(`#${targettedWeekday}StartTime`);
  const $dayEndTime = $(`#${targettedWeekday}EndTime`);
  if ($eventTarget.hasClass('active')) {
    weekDayList.remove(targettedWeekday);
    $eventTarget.removeClass('active');
    $dayStartTime[0].disabled = true;
    $dayEndTime[0].disabled = true;
  } else {
    weekDayList.push(targettedWeekday);
    $eventTarget.addClass('active');
    $dayStartTime[0].disabled = false;
    $dayEndTime[0].disabled = false;
  }
  $weekdaysInput.val(String(weekDayList));
  calculateNumberOfSessions()
}

function handleLessonTimeSlotTypeSelect(event) {
  $("#flexible-time-slot").removeClass('selected');
  $("#fixed-time-slot").removeClass('selected');
  $(event.target).addClass('selected');
  $("#slot_type").val(event.currentTarget.dataset.slotType);
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */

  $('.week-days').click(handleSesionDaysSelect);

  var array = ["2021-01-15", "2021-01-16", "2021-01-17"];
  $( "#startDatepicker" ).datepicker({
    beforeShowDay: function(date){
      var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
      return [ array.indexOf(string) == -1 ]
    },
    onSelect: function() {
      calculateNumberOfSessions();
    }
  });
  $( "#endDatepicker" ).datepicker({
    beforeShowDay: function(date){
      var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
      return [ array.indexOf(string) == -1 ]
    },
    onSelect: function() {
      calculateNumberOfSessions();
    }
  });
  $('.timepicker').timepicker({ 'timeFormat': 'h:i A' });


  $('#pricePerSessionCheck').change(function() {
    if(this.checked) {
      $('#pricePerSessionCurrency')[0].disabled = false;
      $('#pricePerSessionValue')[0].disabled = false;        
    } else {
      $('#pricePerSessionCurrency')[0].disabled = true;
      $('#pricePerSessionValue')[0].disabled = true;        
    }
  })
  $('#weeklyPriceCheck').change(function() {
    if(this.checked) {
      $('#weeklyPriceCurrency')[0].disabled = false;
      $('#weeklyPriceValue')[0].disabled = false;        
    } else {
      $('#weeklyPriceCurrency')[0].disabled = true;
      $('#weeklyPriceValue')[0].disabled = true;        
    }
  })
  $('#monthlyPriceCheck').change(function() {
    if(this.checked) {
      $('#monthlyPriceCurrency')[0].disabled = false;
      $('#monthlyPriceValue')[0].disabled = false;        
    } else {
      $('#monthlyPriceCurrency')[0].disabled = true;
      $('#monthlyPriceValue')[0].disabled = true;        
    }
  })

  $('#pricePerSessionValue').change(function() {
    const selectedCurrency = $('#pricePerSessionCurrency')[0].value;
    const pricePerSessionValue = $('#pricePerSessionValue')[0].value;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#pricePerSessionTotalPrice').text(`${currency} ${pricePerSessionValue}`);
  })

  $('#weeklyPriceValue').change(function() {
    const selectedCurrency = $('#monthlyPriceCurrency')[0].value;
    const pricePerSessionValue = $('#weeklyPriceValue')[0].value;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#weeklyPriceTotalPrice').text(`${currency} ${pricePerSessionValue}`);
  })

  $('#monthlyPriceValue').change(function() {
    const selectedCurrency = $('#monthlyPriceCurrency')[0].value;
    const pricePerSessionValue = $('#monthlyPriceValue')[0].value;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#monthlyPriceTotalPrice').text(`${currency} ${pricePerSessionValue}`);
  })

  $('#lcs2Proceed').click(handleLCS2Proceed);
  /*
      Step2 Time Slot Selection
  */
 $('#flexible-time-slot').click(handleLessonTimeSlotTypeSelect);
  $('#fixed-time-slot').click(handleLessonTimeSlotTypeSelect);
}

init();