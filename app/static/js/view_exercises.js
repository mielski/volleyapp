
function getTrainingId() {
    return Cookies.get("training_id");
}
function add_exercise(button) {
    // adds the current exercise to the active training id
    let trainingId = getTrainingId()
    let exerciseId = button.closest(".col").data("exercise-id")
    console.log("Adding exercise " + exerciseId + " to training " + trainingId);

    $.ajax({ url: `/api/actions/${trainingId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                action_type: 'append',
                position: 0,
                arg: exerciseId
            }),
            success: function (response) {
                console.log(response);
            },
            error: function (response) {
                console.error("problem")
                console.log(response);
            }
    })
}

$(function () {

    $(".button-add-exercise").click(function(event)  {
        let button = $(this);
        button.html("<i class=\"fa-solid fa-check\"></i>");
        button.prop("disabled", true)
        add_exercise(button)
    })

})