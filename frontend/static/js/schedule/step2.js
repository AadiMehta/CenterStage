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
  $('#pricePerSessionError').hide();
  $('#weeklyPriceError').hide();
  $('#monthlyPriceError').hide();
  const startDate = $('#startDatepicker')[0].value;
  const endDate = $('#endDatepicker')[0].value;
  const timezone = $('#timezoneSelect')[0].value;
  const $weekdaysInput = $('#weekdaysInput');
  let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];

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

  const priceType = $('#priceType')[0].value
  const priceCurrency = $(`#${priceType}Currency`)[0].value
  const priceValue = parseInt($(`#${priceType}Value`)[0].value)
  if (!priceCurrency || !priceValue) {
    $(`#${priceType}Error`).text('Please Provide Price');
    $(`#${priceType}Error`).show()
    isValid = false;  
  } else {
    $('#priceCurrency')[0].value = priceCurrency;
    $('#priceValue')[0].value = priceValue;
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
  console.log($eventTarget.hasClass('active'));
  if ($eventTarget.hasClass('active')) {
    weekDayList.pop(targettedWeekday);
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

function enablePriceCheck(name) {
  $('#priceType')[0].value = name;
  $(`#${name}Check`)[0].checked = true;
  $(`#${name}Currency`)[0].disabled = false;
  $(`#${name}Value`)[0].disabled = false;            
}

function disablePriceCheck(name) {
  $(`#${name}Check`)[0].checked = false;
  $(`#${name}Currency`)[0].disabled = true;
  $(`#${name}Value`)[0].disabled = true;
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
      enablePriceCheck('pricePerSession');
      disablePriceCheck('weeklyPrice');
      disablePriceCheck('monthlyPrice');
    } else {
      this.checked = true;
    }
  })
  $('#weeklyPriceCheck').change(function() {
    if(this.checked) {
      disablePriceCheck('pricePerSession');
      enablePriceCheck('weeklyPrice');
      disablePriceCheck('monthlyPrice');
    } else {
      this.checked = true;
    }
  })
  $('#monthlyPriceCheck').change(function() {
    if(this.checked) {
      disablePriceCheck('pricePerSession');
      disablePriceCheck('weeklyPrice');
      enablePriceCheck('monthlyPrice');
    } else {
      this.checked = true;
    }
  })

  $('#pricePerSessionValue').change(function() {
    const selectedCurrency = $('#pricePerSessionCurrency')[0].value;
    const pricePerSessionValue = $('#pricePerSessionValue')[0].value;
    const noOfSessions = parseInt($('#noOfSessions')[0].value);
    const totalPrice = pricePerSessionValue * noOfSessions;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#totalPrice')[0].value = totalPrice;
    $('#pricePerSessionTotalPrice').text(`${currency} ${totalPrice}`);
  })

  $('#weeklyPriceValue').change(function() {
    const selectedCurrency = $('#monthlyPriceCurrency')[0].value;
    const pricePerSessionValue = $('#weeklyPriceValue')[0].value;
    const startDate = $('#startDatepicker').val()
    const endDate = $('#endDatepicker').val()
    const start = dateFns.parse(startDate, 'dd/MM/yyyy', new Date())
    const end = dateFns.parse(endDate, 'dd/MM/yyyy', new Date())
    const weekCount = dateFns.differenceInCalendarWeeks(end, start)
    const totalPrice = pricePerSessionValue * weekCount;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#totalPrice')[0].value = totalPrice;
    $('#weeklyPriceTotalPrice').text(`${currency} ${totalPrice}`);
  })

  $('#monthlyPriceValue').change(function() {
    const selectedCurrency = $('#monthlyPriceCurrency')[0].value;
    const pricePerSessionValue = $('#monthlyPriceValue')[0].value;
    const startDate = $('#startDatepicker').val()
    const endDate = $('#endDatepicker').val()
    const start = dateFns.parse(startDate, 'dd/MM/yyyy', new Date())
    const end = dateFns.parse(endDate, 'dd/MM/yyyy', new Date())
    const daysCount = dateFns.differenceInCalendarDays(end, start)
    let monthCount = dateFns.differenceInCalendarMonths(end, start)
    if (daysCount < 31 && daysCount > 1) {
      monthCount = 1
    }
    const totalPrice = pricePerSessionValue * monthCount;
    const currency = selectedCurrency === 'DOLLARS' ? '$' : '₹';
    $('#totalPrice')[0].value = totalPrice;
    $('#monthlyPriceTotalPrice').text(`${currency} ${totalPrice}`);
  })

  $('#lcs2Proceed').click(handleLCS2Proceed);
  /*
   * Step2 Time Slot Selection
   */
 $('#flexible-time-slot').click(handleLessonTimeSlotTypeSelect);
  $('#fixed-time-slot').click(handleLessonTimeSlotTypeSelect);
}

function updateCopySameTime($eventTarget) {
  if ($eventTarget.hasClass('active')) {
    $eventTarget.removeClass('active');
  } else {
    $eventTarget.addClass('active');
    const $weekdaysInput = $('#weekdaysInput');
    let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];
    if (weekDayList.length > 1) {
      const firstSelectedDay = weekDayList[0]
      const firstSelectedDayStartTime = $(`#${firstSelectedDay}StartTime`)[0].value
      const firstSelectedDayEndTime = $(`#${firstSelectedDay}EndTime`)[0].value      
      const otherSelectedDays = weekDayList.slice(1);
      otherSelectedDays.map((day) => {
        $(`#${day}StartTime`)[0].value = firstSelectedDayStartTime;
        $(`#${day}EndTime`)[0].value = firstSelectedDayEndTime;
      })
    }
  }
}

$('#copySameTime').click((event) => {
  updateCopySameTime($(event.target));
});

init();