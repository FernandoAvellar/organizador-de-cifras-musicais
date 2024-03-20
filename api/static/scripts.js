// Script to ativar classe dark do tailwind de acordo com a preferência do usuário ou do navegador
if (
    localStorage.getItem("color-theme") === "dark" ||
  (!("color-theme" in localStorage) &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  document.documentElement.classList.add("dark");
} else {
  document.documentElement.classList.remove("dark");
}

// Script to deal with light/dark modes selection
    var themeToggleDarkIcon = document.getElementById(
        "theme-toggle-dark-icon"
    );
    var themeToggleLightIcon = document.getElementById(
        "theme-toggle-light-icon"
    );

    // Change the icons inside the button based on previous settings
    if (localStorage.getItem("color-theme") === "dark" ||
        (!("color-theme" in localStorage) &&
            window.matchMedia("(prefers-color-scheme: dark)").matches)
        ) {
          themeToggleLightIcon.classList.remove("hidden");
        } else {
          themeToggleDarkIcon.classList.remove("hidden");
        }

    var themeToggleBtn = document.getElementById("theme-toggle");

    themeToggleBtn.addEventListener("click", function () {
        // toggle icons inside button
        themeToggleDarkIcon.classList.toggle("hidden");
        themeToggleLightIcon.classList.toggle("hidden");

        // if set via local storage previously
    if (localStorage.getItem("color-theme")) {
        if (localStorage.getItem("color-theme") === "light") {
              document.documentElement.classList.add("dark");
              localStorage.setItem("color-theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("color-theme", "light");
        }

        // if NOT set via local storage previously
    } else {
        if (document.documentElement.classList.contains("dark")) {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("color-theme", "light");
        } else {
            document.documentElement.classList.add("dark");
            localStorage.setItem("color-theme", "dark");
            }
        }
    });

window.onload = function() {
  loadFileContent();
  addDeleteUpdateListener();
  addShowSheetMusicPopup();
};


function loadFileContent() {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        generate_textarea_filecontext = document.getElementById("file-content");
        if (generate_textarea_filecontext) {
            document.getElementById("file-content").value = xhr.responseText;
        }
      }
    }
  };
  xhr.open('GET', '/static/cifras_selecionadas.txt', true);
  xhr.send();
}


function addDeleteUpdateListener() {
  var deleteLinks = document.querySelectorAll('.delete-link');
  var updateLinks = document.querySelectorAll('.update-link');

  deleteLinks.forEach(function(link) {
    link.addEventListener('click', function(event) {
      event.preventDefault();
      var cifraId = link.getAttribute('data-cifra-id');
      var confirmDelete = confirm("Are you sure you want to DELETE this sheet music?");
      if (confirmDelete) {
        window.location.href = "/delete/" + cifraId;
      }
    });
  });

  updateLinks.forEach(function(link) {
    link.addEventListener('click', function(event) {
      event.preventDefault();
      var cifraId = link.getAttribute('data-cifra-id');
      var confirmUpgrade = confirm("Are you sure you want to UPDATE this sheet music?");
      if (confirmUpgrade) {
        window.location.href = "/edit/" + cifraId;
      }
    });
  });     
}


function addShowSheetMusicPopup() {
  document.querySelectorAll('.name-cell').forEach(function(cell) {
    cell.addEventListener('click', function() {
      var cifraId = cell.getAttribute('data-cifra-id');
      // Make AJAX request to get cifra content
      fetch('/cifra/' + cifraId)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.text(); // Retorna o conteúdo da resposta como texto
        })
        .then(data => {
          // Display cifra content in popup
          console.log(data);
          document.getElementById('cifra-content').innerText = data;
          document.getElementById('popup-container').classList.remove('hidden');
          document.getElementById('close-popup').addEventListener('click', function() {
              document.getElementById('popup-container').classList.add('hidden');
          });
        })
        .catch(error => {
          console.error('Error:', error);
        });
    });
  });
};


  