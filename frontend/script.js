document.addEventListener("DOMContentLoaded", () => {
  gsap.registerPlugin(ScrollTrigger);

  // Fade-in on load
  document.body.classList.add("fade-in");

  // Hero animations
  gsap.from(".hero-content", {
    opacity: 0,
    y: 50,
    duration: 1.5,
    ease: "power3.out"
  });

  // Engine cards animation
  gsap.utils.toArray(".engine-card").forEach((card, i) => {
    gsap.from(card, {
      scrollTrigger: { trigger: card, start: "top 85%" },
      opacity: 0,
      y: 100,
      duration: 1.2,
      delay: i * 0.15,
      ease: "power3.out"
    });
  });

  // Feature cards animation
  gsap.utils.toArray(".feature-card").forEach((card, i) => {
    gsap.from(card, {
      scrollTrigger: { trigger: card, start: "top 90%" },
      opacity: 0,
      scale: 0.8,
      duration: 1,
      delay: i * 0.1,
      ease: "elastic.out(1, 0.6)"
    });
  });

  // Vanta Background - applied globally
  VANTA.NET({
    el: "body",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.0,
    scaleMobile: 1.0,
    color: 0x00f5a0,
    backgroundColor: 0x0a0f1c,
    points: 14.0,
    maxDistance: 22.0,
    spacing: 16.0
  });

  // Smooth transition to factcheck.html
  const factCheckBtn = document.querySelector(".btn.primary");
  if (factCheckBtn) {
    factCheckBtn.addEventListener("click", (e) => {
      e.preventDefault();
      document.body.classList.remove("fade-in");
      document.body.classList.add("fade-out");
      setTimeout(() => {
        window.location.href = "factcheck.html";
      }, 400); // matches CSS transition
    });
  }
});
