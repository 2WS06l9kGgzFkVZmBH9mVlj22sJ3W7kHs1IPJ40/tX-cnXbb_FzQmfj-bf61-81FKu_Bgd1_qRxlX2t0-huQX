      // Form submission
      document.getElementById('contact-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var form = event.target;
        var formData = new FormData(form);
        fetch(form.action, {
          method: form.method,
          headers: {
            'Accept': 'application/json'
          },
          body: formData
        }).then(response => {
          if (response.ok) {
            alert('Thank you for your message! I will get back to you soon.');
            form.reset();
          } else {
            response.json().then(data => {
              if (data.errors) {
                alert('Oops! There was a problem submitting your form: ' + data.errors.map(error => error.message).join(', '));
              } else {
                alert('Oops! There was a problem submitting your form.');
              }
            });
          }
        }).catch(error => {
          alert('Oops! There was a problem submitting your form. Error: ' + error.message);
        });
      });
      const burgerMenu = document.querySelector('.burger-menu');
      const navMenu = document.querySelector('.nav-menu');
      burgerMenu.addEventListener('click', () => {
        burgerMenu.classList.toggle('active');
        navMenu.classList.toggle('active');
      });
      document.querySelectorAll('.nav-menu li a').forEach(n => n.addEventListener('click', () => {
        burgerMenu.classList.remove('active');
        navMenu.classList.remove('active');
      }));

      document.addEventListener('DOMContentLoaded', (event) => {
        const modal = document.getElementById('videoModal');
        const videoPlayer = document.querySelector('.youtube-player');
        const closeBtn = document.querySelector('.close');
        const playButtons = document.querySelectorAll('.play-button');

        function getYouTubeEmbedUrl(url) {
          const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
          const match = url.match(regExp);
          if (match && match[2].length === 11) {
            return `https://www.youtube.com/embed/${match[2]}`;
          }
          return null;
        }
        playButtons.forEach(button => {
          button.addEventListener('click', () => {
            const videoUrl = button.getAttribute('data-video-url');
            const embedUrl = getYouTubeEmbedUrl(videoUrl);
            if (embedUrl) {
              videoPlayer.src = `${embedUrl}?autoplay=1`;
              modal.style.display = 'block';
            } else {
              console.error('Invalid YouTube URL');
            }
          });
        });
        closeBtn.addEventListener('click', () => {
          modal.style.display = 'none';
          videoPlayer.src = '';
        });
        window.addEventListener('click', (event) => {
          if (event.target == modal) {
            modal.style.display = 'none';
            videoPlayer.src = '';
          }
        });
      });