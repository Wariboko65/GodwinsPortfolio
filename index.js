// Connect to Google Sheet
    const scriptURL = 'https://script.google.com/macros/s/AKfycbymenROw-xordeZtvMS0kc0iD8z_NkB2wNW_m0TyY5VpJMjYfWMXVmyjwL0GTGRbY8M2w/exec'
    const form = document.forms['submit-to-google-sheet']
    const msg = document.getElementById("msg")

    form.addEventListener('submit', e => {
    e.preventDefault();
    fetch(scriptURL, { method: 'POST', body: new FormData(form)})
        .then(response => {
            msg.innerHTML = "Message sent successfully";
            setTimeout(function(){
                msg.innerHTML = "";
            }, 5000)
            form.reset();
        })
        .catch(error => console.error('Error!', error.message));
    });
// Connected to Google Sheet Successfully

// Change Navigation on Scroll
    const nav = document.querySelector("nav");
    const sectionOne = document.querySelector(".top");

    const sectionOneOptions = {
        rootMargin: "-90% 0px 0px 0px"
    };

    const sectionOneObserver = new IntersectionObserver(function(
        entries,
        sectionOneObserver
    ) {
        entries.forEach(entry => {
            if(!entry.isIntersecting) {
                nav.classList.add("navv")
            } else {
                nav.classList.remove("navv");
            }
        })
    },
    sectionOneOptions);

    sectionOneObserver.observe(sectionOne);
// Changed Navigation on Scroll Successfully

// Fade content into Viewport on Scroll
    const faders =  document.querySelectorAll(".fade-in");
    const sliders = document.querySelectorAll(".slide-in");
    
    const appearOptions = {
      threshold: 0,
      rootMargin: "0px 0px -250px 0px"
    };
    
    const appearOnScroll = new IntersectionObserver
    (function(
      entries, 
      appearOnScroll
    ) {
    entries.forEach(entry => {
      if (!entry.isIntersecting) {
        return;
        } else {
          entry.target.classList.add("appear");
          appearOnScroll.unobserve(entry.target);
        }
      }) 
    },
    appearOptions); 
    
    faders.forEach(fader => { 
      appearOnScroll.observe(fader);
    });
     
    sliders.forEach(slider => {
      appearOnScroll.observe(slider);
    });
// Faded content into Viewport on Scroll Successfully

// Change, Store and Retrieve Theme
    const toggleButton = document.querySelector("#light-dark-toggle");
    let imagex = document.body;
    let darkBackground = document.querySelector(".top");
    let themeIcon = document.getElementById("change-icon");
    let navText = document.getElementById("nav-change");

    const navTextChanger = document.querySelector("#nav-change");
    const storedValues = localStorage.getItem("theme");

        function changeTheme() {
            if (localStorage.getItem("theme") === "light") {
                localStorage.setItem("theme", "dark");
                document.body.classList.add("dark");
                document.body.classList.remove("light");
                themeIcon.classList.add("bi-sun-fill");
                themeIcon.classList.remove("bi-moon-fill");
                navText.classList.add("navbar-dark");
                navText.classList.remove("navbar-light");
                darkBackground.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
            } else {
                localStorage.setItem("theme", "light");
                document.body.classList.add("light");
                document.body.classList.remove("dark");
                themeIcon.classList.add("bi-moon-fill");
                themeIcon.classList.remove("bi-sun-fill");
                navText.classList.add("navbar-light");
                navText.classList.remove("navbar-dark");
                darkBackground.style.backgroundColor = "rgba(0, 0, 0, 0)";
            }
        }

        toggleButton.addEventListener("click", () => {
            changeTheme();
        });

        window.addEventListener("load", () => {
        const storedTheme = localStorage.getItem("theme");
        const navChanger = document.getElementById("nav-change");

            if (storedTheme) {
                document.body.classList.add(storedTheme);
        
            } else {
                localStorage.setItem("theme", "light");
            }
        });

        window.addEventListener("load", () => {
            if (storedValues === "light") {
                navTextChanger.classList.add("navbar-light");
                themeIcon.classList.add("bi-moon-fill");
            } else {
                navTextChanger.classList.add("navbar-dark");
                themeIcon.classList.add("bi-sun-fill");
                darkBackground.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
            }
        });
// Change, Store and Retrieve Theme