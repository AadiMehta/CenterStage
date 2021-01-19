

  
// ****** Event Handlers ****** 


function handleLCS4Proceed() {
  let isValid = true;
  $('#goalError').hide();
  $('#requirementError').hide();

  const goals = [];
  const requirements = [];
  $('.goal-input').map((item, goalInput) => {
    if (goalInput.value) {
      goals.push(goalInput.value)
    }
  });

  $('.requirement-input').map((item, requirementInput) => {
    if (requirementInput.value) {
      requirements.push(requirementInput.value)
    }
  });

  if (goals.length === 0) {
    $('#goalError').text('Add Atleast One Goal');
    $('#goalError').show()
    isValid = false;
  }
  if (requirements.length === 0) {
    $('#requirementError').text('Add Atleast One Requirement');
    $('#requirementError').show()
    isValid = false;
  }
  if (isValid) {
    $('#goals').val(JSON.stringify(goals));
    $('#requirements').val(JSON.stringify(requirements));
    $("#step4").submit();
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

function addMoreRequirement() {
  const newRequirementInput = $('#referenceRequirementInput').clone();
  const { index } = newRequirementInput.data();
  if (index === 5) {
    return;
  }
  const lastRequirementInput = $("#lastRequirementInput");
  newRequirementInput.insertBefore(lastRequirementInput);
  newRequirementInput.find('input').val(lastRequirementInput.find('input').val());
  newRequirementInput.find('input').attr('data-requirement-index', index - 1);
  newRequirementInput.find('input').addClass('requirement-input');
  newRequirementInput.find('input').attr('data-requirement-index', index);
  lastRequirementInput.find('input').val('')
  newRequirementInput.show();
  $('#referenceRequirementInput').attr('data-index', index + 1);
}

  
// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  $('#addMoreGoalButton').click(addMoreGoal);
  $('#lastGoalInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreGoal();
    }
  });
  $('#addMoreRequirementButton').click(addMoreRequirement);
  $('#lastRequirementInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreRequirement();
    }
  });

  $('#lcs4Proceed').click(handleLCS4Proceed);
}

init();