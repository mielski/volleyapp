$(document).ready(function() {
    $('.move-up, .move-down').on('click', function() {
        var $exercise = $(this).closest('.exercise');
        var exerciseId = $exercise.data('exercise-id');
        var currentPosition = $exercise.data('position');
        var newPosition = currentPosition;

        if ($(this).hasClass('move-up')) {
            newPosition -= 1;
        } else if ($(this).hasClass('move-down')) {
            newPosition += 1;
        }

        // Make AJAX request to update the order in the database
        $.ajax({
            url: '/update_order',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                exercise_id: exerciseId,
                new_position: newPosition
            }),
            success: function(response) {
                if (response.status === 'success') {
                    // Update the position data attribute
                    $exercise.data('position', newPosition);

                    // Rearrange the elements on the page
                    if (newPosition < currentPosition) {
                        $exercise.insertBefore($exercise.prev());
                    } else {
                        $exercise.insertAfter($exercise.next());
                    }

                    // Optionally, add some animation
                    $exercise.css('transform', 'scale(1.05)');
                    setTimeout(function() {
                        $exercise.css('transform', 'scale(1)');
                    }, 300);
                }
            }
        });
    });
});
