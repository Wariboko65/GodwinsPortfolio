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

