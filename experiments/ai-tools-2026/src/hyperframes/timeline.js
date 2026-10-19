(() => {
  const boundary = [0, 9.6, 25.15, 34.2, 43.55, 53.45, 64.9, 73.8];

  window.__buildAIToolsTimeline = () => {
    const tl = gsap.timeline({ paused: true });
    const proxy = { progress: 0 };

    tl.to(
      proxy,
      {
        progress: 1,
        duration: 73.8,
        ease: "none",
        onUpdate: () => window.__aiTools3D?.renderAt(proxy.progress),
      },
      0,
    );

    const enter = (selector, at, vars = {}) => {
      tl.fromTo(
        selector,
        { opacity: 0, y: 48, ...vars.from },
        {
          opacity: 1,
          y: 0,
          duration: 0.72,
          stagger: 0.12,
          ease: "power3.out",
          ...vars.to,
        },
        at,
      );
    };

    enter("#method .kicker", 0.22);
    enter("#method .display .line", 0.4, { to: { stagger: 0.14 } });
    enter("#method .hairline", 1.05, {
      from: { scaleX: 0, opacity: 1, y: 0 },
      to: { scaleX: 1, duration: 0.9, ease: "power2.inOut" },
    });
    enter("#method .metric-lockup", 1.35);
    enter("#method .not-users", 2.25);
    enter("#method .source-line", 2.85);

    enter("#ranking .kicker", boundary[1] + 0.12);
    enter("#ranking .ranking-title", boundary[1] + 0.28);
    enter("#ranking .ranking-date", boundary[1] + 0.48);
    tl.fromTo(
      "#ranking .bar-row",
      { opacity: 0, x: -55 },
      {
        opacity: 1,
        x: 0,
        duration: 0.62,
        stagger: 0.18,
        ease: "power3.out",
      },
      boundary[1] + 0.82,
    );
    tl.fromTo(
      "#ranking .bar-fill",
      { scaleX: 0 },
      {
        scaleX: 1,
        duration: 1.35,
        stagger: 0.18,
        ease: "power3.inOut",
      },
      boundary[1] + 1.05,
    );
    enter("#ranking .ranking-note", boundary[2] - 2.1);

    for (let i = 2; i <= 5; i += 1) {
      const scene = document.querySelector(`#pair-${i - 1}`);
      const at = boundary[i];
      enter(`#${scene.id} .tool-side:first-child .tool-index`, at + 0.1);
      enter(`#${scene.id} .tool-side:last-child .tool-index`, at + 0.22);
      enter(`#${scene.id} .tool-name`, at + 0.35, { to: { stagger: 0.18 } });
      enter(`#${scene.id} .tool-strength`, at + 1.15, { to: { stagger: 0.18 } });
      enter(`#${scene.id} .tool-use`, at + 1.75, { to: { stagger: 0.18 } });
      enter(`#${scene.id} .tool-meta`, at + 2.35, { to: { stagger: 0.18 } });
      enter(`#${scene.id} .pair-caption`, at + 2.75);
    }

    enter("#choice .kicker", boundary[6] + 0.1);
    enter("#choice .choice-title", boundary[6] + 0.28);
    tl.fromTo(
      "#choice .choice-item",
      { opacity: 0, y: 38 },
      {
        opacity: 1,
        y: 0,
        duration: 0.62,
        stagger: 0.16,
        ease: "power3.out",
      },
      boundary[6] + 1.15,
    );
    enter("#choice .final-line", boundary[6] + 3.2);
    tl.to(
      "#choice .choice-map",
      { opacity: 0.42, duration: 0.65, ease: "power2.inOut" },
      72.82,
    );

    [9.6, 25.15, 34.2, 43.55, 53.45, 64.9].forEach((time, index) => {
      tl.fromTo(
        `#transition-wipe-${index + 1}`,
        { xPercent: -125 },
        {
          xPercent: 125,
          duration: 0.82,
          ease: "power3.inOut",
          immediateRender: false,
        },
        time - 0.38,
      );
    });

    window.__timelines = window.__timelines || {};
    window.__timelines.main = tl;
  };
})();
