// ****** Event Handlers ****** 

function handleLCS2Proceed() {
  let isValid = true;
  $('#startDatePickerError').hide();
  $('#sessionDatePickerError').hide();
  $('#sessionStartTimePickerError').hide();
  $('#sessionEndTimePickerError').hide();
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
  if (sessionType === 'MULTI') {
    let startDate, endDate, $weekdaysInput, weekDayList, timezone;
    startDate = $('#startDatepicker')[0].value;
    endDate = $('#endDatepicker')[0].value;
    timezone = $('#timezoneSelect')[0].value;
    $weekdaysInput = $('#weekdaysInput');
    weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];
    weekDayList.map((day) => {
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
  } else {
    let sessionDate, sessionStartTime, sessionEndTime;
    sessionDate = $('#sessionDatepicker')[0].value;
    sessionStartTime = $('#sessionStartTimePicker')[0].value;
    sessionEndTime = $('#sessionEndTimePicker')[0].value;
    timezone = $('#timezoneSelect')[0].value;
    if (!sessionDate) {
      $('#sessionDatePickerError').text('Please Select Session Date');
      $('#sessionDatePickerError').show()
      isValid = false;
    }
    if (!sessionStartTime) {
      $('#sessionStartTimePickerError').text('Please Select Session Start Time');
      $('#sessionStartTimePickerError').show()
      isValid = false;
    }
    if (!sessionEndTime) {
      $('#sessionEndTimePickerError').text('Please Select Session End Time');
      $('#sessionEndTimePickerError').show()
      isValid = false;
    }
    if (timezone === 'none') {
      $('#timezoneSelectError').text('Please Select Timezone');
      $('#timezoneSelectError').show()
      isValid = false;
    }  
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
  if (sessionType !== 'MULTI') return;
  const startDate = $('#startDatepicker')[0].value;
  const endDate = $('#endDatepicker')[0].value;
  const $weekdaysInput = $('#weekdaysInput');
  let weekDayList = $weekdaysInput[0].value ? $weekdaysInput[0].value.split(',') : [];

  const startDateObj = dateFns.parse(startDate, 'MM/dd/yyyy', new Date());
  const endDateObj = dateFns.parse(endDate, 'MM/dd/yyyy', new Date());
  endDateObj.setHours(23,59,59,999);
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
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
  $(`#${name}Currency`)[0].value = 'USD';
  $(`#${name}Currency`)[0].disabled = true;
  $(`#${name}Value`)[0].disabled = true;
  $(`#${name}Value`).val(0);
  $(`#${name}TotalPrice`).text('');
}

function handleLessonTimeSlotTypeSelect(event) {
  $("#flexible-time-slot").removeClass('selected');
  $("#fixed-time-slot").removeClass('selected');
  $(event.target).addClass('selected');
  $("#slot_type").val(event.currentTarget.dataset.slotType);
}

function handleMonthlyPriceChange() {
  const selectedCurrencyEl = $('#monthlyPriceCurrency')[0];
  const selectedCurrency = selectedCurrencyEl.children[selectedCurrencyEl.selectedIndex]
  const pricePerSessionValue = $('#monthlyPriceValue')[0].value;
  const startDate = $('#startDatepicker').val()
  const endDate = $('#endDatepicker').val()
  const start = dateFns.parse(startDate, 'dd/MM/yyyy', new Date())
  const end = dateFns.parse(endDate, 'dd/MM/yyyy', new Date())
  const daysCount = dateFns.differenceInCalendarDays(end, start)
  let monthCount = 1;
  if (daysCount > 1 && daysCount < 31) {
    monthCount = 1
  } else if (sessionType !== 'ONGOING' && sessionType !== 'SINGLE') {
    monthCount = dateFns.differenceInCalendarMonths(end, start)
  }
  const totalPrice = pricePerSessionValue * monthCount;
  const {symbol} = selectedCurrency.dataset;
  $('#totalPrice')[0].value = totalPrice;
  $('#monthlyPriceTotalPrice').text(`${symbol} ${totalPrice}`);
}

function handleWeeklyPriceChange() {
  const selectedCurrencyEl = $('#weeklyPriceCurrency')[0];
  const selectedCurrency = selectedCurrencyEl.children[selectedCurrencyEl.selectedIndex]
  const pricePerSessionValue = $('#weeklyPriceValue')[0].value;
  const startDate = $('#startDatepicker').val()
  const endDate = $('#endDatepicker').val()
  const start = dateFns.parse(startDate, 'dd/MM/yyyy', new Date())
  const end = dateFns.parse(endDate, 'dd/MM/yyyy', new Date())
  let weekCount = 1;
  if (sessionType !== 'ONGOING' && sessionType !== 'SINGLE') {
    weekCount = dateFns.differenceInCalendarWeeks(end, start)  
  }
  const totalPrice = pricePerSessionValue * weekCount;
  const {symbol} = selectedCurrency.dataset;
  $('#totalPrice')[0].value = totalPrice;
  $('#weeklyPriceTotalPrice').text(`${symbol} ${totalPrice}`);
}

function handlePricePerSessionChange() {
  const selectedCurrencyEl = $('#pricePerSessionCurrency')[0];
  const selectedCurrency = selectedCurrencyEl.children[selectedCurrencyEl.selectedIndex]
  const pricePerSessionValue = $('#pricePerSessionValue')[0].value;
  let noOfSessions = 1;
  if (sessionType !== 'ONGOING' && sessionType !== 'SINGLE') {
    noOfSessions = parseInt($('#noOfSessions')[0].value);
  }
  const totalPrice = pricePerSessionValue * noOfSessions;
  const {symbol} = selectedCurrency.dataset;
  $('#totalPrice')[0].value = totalPrice;
  $('#pricePerSessionTotalPrice').text(`${symbol} ${totalPrice}`);
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */

  $('.week-days').click(handleSesionDaysSelect);

  var array = ["2021-01-15", "2021-01-16", "2021-01-17"];
  $( "#sessionDatepicker" ).datepicker({
    minDate: 0,
    beforeShowDay: function(date){
      var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
      return [ array.indexOf(string) == -1 ]
    },
    onSelect: function() {
      $('#startDatePickerError').text('');
      calculateNumberOfSessions();
    }
  });
  $( "#startDatepicker" ).datepicker({
    minDate: 0,
    beforeShowDay: function(date){
      var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
      return [ array.indexOf(string) == -1 ]
    },
    onSelect: function() {
      $('#startDatePickerError').text('');
      calculateNumberOfSessions();
    }
  });
  $( "#endDatepicker" ).datepicker({
    minDate: 0,
    beforeShowDay: function(date){
      var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
      return [ array.indexOf(string) == -1 ]
    },
    onSelect: function() {
      $('#endDatePickerError').text('');
      calculateNumberOfSessions();
    }
  });
  $('.timepicker').timepicker({
    'timeFormat': 'h:i A',
    'scrollDefault': 'now',
    'step': 15
  });

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

  $('.validateendtime').change(function(e) {
    if (!e.target.value) {
      return;
    }
    const { check } = e.target.dataset
    const endValue = moment(e.target.value, 'HH:mm A')
    let startValue = $(`#${check}`)[0].value
    $(`#${e.target.id}Error`).hide();
    $(`#${check}Error`).hide();
    if (!startValue) {
      return;
    }
    startValue = moment(startValue, 'HH:mm A');
    if (moment.duration(endValue.diff(startValue)).minutes() < 0 || moment.duration(endValue.diff(startValue)).hours() < 0) {
      $(`#${e.target.id}Error`).text('Start time should not exceed end time');
      $(`#${e.target.id}Error`).show()
      e.target.value = null;
    }
  });

  $('.validatestarttime').change(function(e) {
    if (!e.target.value) {
      return;
    }
    const { check } = e.target.dataset
    const startValue = moment(e.target.value, 'HH:mm A')
    let endValue = $(`#${check}`)[0].value
    $(`#${e.target.id}Error`).hide();
    $(`#${check}Error`).hide();
    if (!endValue) {
      return;
    }
    endValue = moment(endValue, 'HH:mm A');
    if (moment.duration(endValue.diff(startValue)).minutes() < 0 || moment.duration(endValue.diff(startValue)).hours() < 0) {
      $(`#${e.target.id}Error`).text('Start time should not exceed end time');
      $(`#${e.target.id}Error`).show()
      e.target.value = null;
    }
  });

  $('#pricePerSessionCurrency').change(handlePricePerSessionChange)
  $('#pricePerSessionValue').change(handlePricePerSessionChange)
  $('#weeklyPriceCurrency').change(handleWeeklyPriceChange)
  $('#weeklyPriceValue').change(handleWeeklyPriceChange)
  $('#monthlyPriceCurrency').change(handleMonthlyPriceChange)
  $('#monthlyPriceValue').change(handleMonthlyPriceChange)

  $('#lcs2Proceed').click(handleLCS2Proceed);
  /*
   * Step2 Time Slot Selection
   */
  $('#flexible-time-slot').click(handleLessonTimeSlotTypeSelect);
    $('#fixed-time-slot').click(handleLessonTimeSlotTypeSelect);
  }

  $('#timezoneSelect').change((event) => {
    if (event.target.value !== 'none') {
      $('#timezoneSelectError').text('');
    }
  })
  $('#pricePerSessionValue').bind('keyup input', function(event){
    if (event.target.value) {
      $('#pricePerSessionError').text('');
    }
  });
  $('#weeklyPriceValue').bind('keyup input', function(event){
    if (event.target.value) {
      $('#weeklyPriceError').text('');
    }
  });
  $('#monthlyPriceValue').bind('keyup input', function(event){
    if (event.target.value) {
      $('#monthlyPriceError').text('');
    }
  });

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