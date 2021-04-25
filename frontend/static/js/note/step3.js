
function handleNTS3Proceed() {
  let isValid = true;
  const priceType = $('#priceType')[0].value
  const priceCurrency = $(`#${priceType}Currency`)[0].value
  const priceValue = parseInt($(`#${priceType}Value`)[0].value)
  $('#priceCurrency')[0].value = priceCurrency;
  $('#priceValue')[0].value = priceValue;
  $('#goalError').hide();
  const goals = [];
  $('.goal-input').map((item, goalInput) => {
    if (goalInput.value) {
      goals.push(goalInput.value)
    }
  });
   if (goals.length === 0) {
    $('#goalError').text('Add Atleast One Goal');
    $('#goalError').show()
    isValid = false;
  }
  if (isValid) {
    $('#goals').val(JSON.stringify(goals));
    $("#step3").submit();
  }
}

function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function(e) {
      $('#previewCoverImage').attr('src', e.target.result);
      $('#previewCoverImageDataUrl')[0].value = e.target.result;
    }
    reader.readAsDataURL(input.files[0]);
  }
}

function addMoreGoal() {
  const newGoalInput = $('#referenceGoalInput').clone();
  const { index } = newGoalInput.data();
  if (index === 5) {
    return;
  }
  const lastGoalInput = $("#lastGoalInput");
  newGoalInput.insertBefore(lastGoalInput);
  newGoalInput.find('input').val(lastGoalInput.find('input').val());
  newGoalInput.find('input').attr('data-goal-index', index - 1);
  newGoalInput.find('input').addClass('goal-input');
  lastGoalInput.find('input').attr('data-goal-index', index);
  lastGoalInput.find('input').val('')
  newGoalInput.show();
  $('#referenceGoalInput').attr('data-index', index + 1);
}


function init() {


$('#notePriceValue').change(function() {
    const selectedCurrency = $('#notePriceCurrency')[0].value;
    const notePriceValue = $('#notePriceValue')[0].value;
  });
$("#coverImageUpload").change(function() {
    readURL(this);
  });

$('#addMoreGoalButton').click(addMoreGoal);
$('#lastGoalInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreGoal();
    }
  });
$('#nts3Proceed').click(handleNTS3Proceed);
}

init();