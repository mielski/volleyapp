const fileTypes = [
  "image/apng",
  "image/bmp",
  "image/gif",
  "image/jpeg",
  "image/pjpeg",
  "image/png",
  "image/svg+xml",
  "image/tiff",
  "image/webp",
  "image/x-icon",
];

function validFileType(file) {
  return fileTypes.includes(file.type);
}

function returnFileSize(number) {
  if (number < 1e3) {
    return `${number} bytes`;
  } else if (number >= 1e3 && number < 1e6) {
    return `${(number / 1e3).toFixed(1)} KB`;
  } else {
    return `${(number / 1e6).toFixed(1)} MB`;
  }
}
function updateImageDisplay() {
    const preview = $(".preview");
    const input = $("#image_uploads");
    preview.empty()


  const curFiles = input[0].files;
  if (curFiles.length === 0) {
    const para = $("<p>");
    para.text = "No files currently selected for upload";
    preview.append(para);
  } else {
    const list =$("<ol>");
    preview.append(list);

    for (const file of curFiles) {
      const listItem = document.createElement("li");
      const para = document.createElement("p");
      if (validFileType(file)) {
        para.textContent = `File name ${file.name}, file size ${returnFileSize(
          file.size,
        )}.`;
        const image = document.createElement("img");
        image.src = URL.createObjectURL(file);
        image.alt = image.title = file.name;

        listItem.appendChild(image);
        listItem.appendChild(para);
      } else {
        para.textContent = `File name ${file.name}: Not a valid file type. Update your selection.`;
        listItem.appendChild(para);
      }

      list.append($(listItem));
    }
  }


}


$(function () {

  const input = $("#image_uploads");


  input[0].style.opacity = 0;
  input.change(updateImageDisplay)

  function putImagesToExercise(event) {
      let formDataImage = new FormData($("form")[0]);
      let exerciseId = $("#submit").data("exercise-id")
      formDataImage.append('images', input[0].files[0]); // Assuming fileInput is your file input element
      $.ajax({
        url: `/api/exercises/${exerciseId}/images`,
        type: "PUT",
        data: formDataImage,
        processData: false,
        contentType: false,
        success: function (response) {
          console.log('Image uploaded successfully:', response);
        },
        error: function (xhr, status, error) {
          console.error('Error uploading image:', error);
        }
      })
    }


})