function get_training_id() {
    // Gets the training id from the url
    var path = window.location.pathname;
    return path.split("/")[2]
}

function update_button_status() {
    // ensure the first move-up button and last move-down button is disabled.

    const buttonUpList = $(".button-move-up");
    const buttonDownList = $(".button-move-down");
    console.log("call update_button_status")

    if (buttonUpList.length == 0) {
        console.log("no buttons found -> ending function")
        return;
    }

    // change button up list
    buttonUpList.prop("disabled", false);
    buttonUpList.first().prop("disabled", true);

    // change the button down list
    buttonDownList.prop("disabled", false);
    buttonDownList.last().prop("disabled", true);


}

$(document).ready(function () {

    // add functionality to the move up and move down buttons, doing ajax call to change order and shifting the
    // elements
    $('.button-move-up, .button-move-down').on('click', function () {
        var $exercise = $(this).closest('.row');
        var currentPosition = $exercise.index();
        var newPosition = currentPosition;

        var trainingId = get_training_id();


        if ($(this).hasClass('button-move-up')) {
            newPosition -= 1;
        } else if ($(this).hasClass('button-move-down')) {
            newPosition += 1;
        }

        // Make AJAX request to update the order in the database
        $.ajax({
            url: `/api/actions/${trainingId}/`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                action_type: 'reorder',
                position: currentPosition,
                arg: String(newPosition)
            }),
            success: function (response) {
                if (response.status === 'success') {
                    // Update the position data attribute
                    // $exercise.data('position', newPosition);
                    $exercise.slideUp(400, function () {
                        // Rearrange the elements on the page
                        if (newPosition < currentPosition) {
                            $exercise.insertBefore($exercise.prev())
                        } else {
                            {
                                $exercise.insertAfter($exercise.next())
                            }
                        }
                        $exercise.slideDown(400);
                        // Optionally, add some animation
                        // $exercise.css('font-weight', 'bold');
                        // setTimeout(function() {
                        //     $exercise.css('font-weight', 'inherit');
                        // }, 300);
                        update_button_status()
                    })
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                console.log(error.description)
            }

        })

    })
    update_button_status();

    $(".button-delete").click( function () {
        //remove the current exercise from the training
        const trainingId = get_training_id();
        const exerciseRow =   $(this).closest(".row");
        let position = exerciseRow.prevAll().length;
        let exerciseId = exerciseRow.data("exercise-id");
        let data = {
                position: position,
                action_type: "remove",
            };
        console.log("action data:");
        console.log(data);
        $.ajax({
            url: `/api/actions/${trainingId}`,
            method: "POST",
            contentType: "Application/JSON",
            data: JSON.stringify(data),
            success: function(response) {
                console.log("success response:");
                console.log(response);
                exerciseRow.slideUp(400, function (){exerciseRow.remove()});
            },
            error: function (response)  {
                console.error(response);
            }

        });


    })

    // add functionality to the plus sign to add cookie to the browser with training id
    $("#btn-add-exercises").click( function(event) {
        Cookies.set("training_id", get_training_id())
        console.log(Cookies.get("training_id"))
    })

})