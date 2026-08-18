/**
 * Realistic Client-Side Interactive 3D World Globe Component
 * Features:
 * - Deep Blue Gradient Oceans & Specular Atmospheric Glow
 * - Realistic Natural Green Continents & Landmass Topography
 * - Latitude / Longitude Graticule Grid Lines
 * - Dynamic Country Markers & Hover Highlights connected to GET /travel/countries
 * - 360° Horizontal Drag, Vertical Tilt, Scroll Zoom, Zoom Buttons & Reset Controls
 * Zero External Paid API Keys Required.
 */

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("globeCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let width = canvas.width = canvas.parentElement.clientWidth || 600;
  let height = canvas.height = canvas.parentElement.clientHeight || 450;

  let radius = Math.min(width, height) * 0.36;
  let rotationX = 0.2; // Slight tilt
  let rotationY = 0;
  let isDragging = false;
  let lastMouseX = 0;
  let lastMouseY = 0;
  let hoveredCountry = null;
  let countriesData = [];

  // Realistic Simplified World Continent Polygon Paths (Lat/Lng coordinates)
  const CONTINENTS = [
    // North America
    [ [70,-160],[70,-60],[50,-55],[45,-65],[30,-80],[25,-80],[15,-90],[10,-83],[15,-105],[30,-115],[48,-125],[60,-140],[65,-168] ],
    // South America
    [ [12,-72],[10,-60],[-5,-35],[-20,-40],[-35,-55],[-55,-68],[-45,-75],[-18,-70],[0,-80] ],
    // Europe
    [ [70,25],[70,40],[60,30],[55,40],[45,35],[36,36],[36,-9],[43,-9],[48,2],[54,9],[60,5],[65,15] ],
    // Africa
    [ [37,10],[32,32],[12,43],[0,42],[-12,40],[-34,26],[-34,18],[-10,13],[5,9],[5,-15],[15,-17],[30,-10],[37,10] ],
    // Asia
    [ [75,60],[75,170],[60,170],[50,140],[35,140],[22,120],[10,105],[10,78],[25,65],[30,48],[42,44],[50,55],[60,60] ],
    // Australia & Oceania
    [ [-12,130],[-15,145],[-35,150],[-38,140],[-32,115],[-20,114] ],
    // Antarctica
    [ [-65,-180],[-65,-90],[-65,0],[-65,90],[-65,180],[-85,180],[-85,-180] ]
  ];

  // Fetch country data from backend API
  fetch("/travel/countries")
    .then(res => res.json())
    .then(data => {
      countriesData = data;
      render();
    })
    .catch(err => console.log("Globe country fetch notice:", err));

  // Handle Window Resize
  window.addEventListener("resize", () => {
    width = canvas.width = canvas.parentElement.clientWidth || 600;
    height = canvas.height = canvas.parentElement.clientHeight || 450;
    radius = Math.min(width, height) * 0.36;
    render();
  });

  // Mouse Drag Handlers
  canvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });

  window.addEventListener("mouseup", () => isDragging = false);

  canvas.addEventListener("mousemove", (e) => {
    if (isDragging) {
      const deltaX = e.clientX - lastMouseX;
      const deltaY = e.clientY - lastMouseY;
      rotationY += deltaX * 0.005;
      rotationX = Math.max(-1.2, Math.min(1.2, rotationX + deltaY * 0.005));
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      render();
    } else {
      checkHover(e);
    }
  });

  // Mouse Wheel Zoom
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    if (e.deltaY < 0) {
      radius = Math.min(radius * 1.08, Math.min(width, height) * 0.48);
    } else {
      radius = Math.max(radius * 0.92, Math.min(width, height) * 0.2);
    }
    render();
  }, { passive: false });

  // Touch Support
  canvas.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) {
      isDragging = true;
      lastMouseX = e.touches[0].clientX;
      lastMouseY = e.touches[0].clientY;
    }
  });

  canvas.addEventListener("touchmove", (e) => {
    if (isDragging && e.touches.length === 1) {
      const deltaX = e.touches[0].clientX - lastMouseX;
      const deltaY = e.touches[0].clientY - lastMouseY;
      rotationY += deltaX * 0.005;
      rotationX = Math.max(-1.2, Math.min(1.2, rotationX + deltaY * 0.005));
      lastMouseX = e.touches[0].clientX;
      lastMouseY = e.touches[0].clientY;
      render();
    }
  });

  canvas.addEventListener("touchend", () => isDragging = false);

  // Zoom & Reset Buttons
  const zoomInBtn = document.getElementById("globeZoomIn");
  const zoomOutBtn = document.getElementById("globeZoomOut");
  const resetBtn = document.getElementById("globeResetView");

  if (zoomInBtn) {
    zoomInBtn.addEventListener("click", () => {
      radius = Math.min(radius * 1.15, Math.min(width, height) * 0.48);
      render();
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", () => {
      radius = Math.max(radius * 0.85, Math.min(width, height) * 0.2);
      render();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      rotationX = 0.2;
      rotationY = 0;
      radius = Math.min(width, height) * 0.36;
      render();
    });
  }

  // Click Navigation
  canvas.addEventListener("click", () => {
    if (hoveredCountry) {
      window.location.href = `/explore?country=${encodeURIComponent(hoveredCountry.name)}`;
    }
  });

  // Convert Latitude / Longitude to 3D Projected Screen Coordinates
  function latLngTo3D(lat, lng) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lng + 180) * (Math.PI / 180);

    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const z = (radius * Math.sin(phi) * Math.sin(theta));
    const y = (radius * Math.cos(phi));

    // Apply rotation matrices
    const cosX = Math.cos(rotationX), sinX = Math.sin(rotationX);
    const cosY = Math.cos(rotationY), sinY = Math.sin(rotationY);

    const x1 = x * cosY - z * sinY;
    const z1 = x * sinY + z * cosY;

    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;

    return {
      x: width / 2 + x1,
      y: height / 2 + y2,
      visible: z2 > 0,
      z: z2
    };
  }

  function checkHover(e) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let found = null;
    for (const c of countriesData) {
      const pos = latLngTo3D(c.latitude, c.longitude);
      if (pos.visible) {
        const dist = Math.hypot(mouseX - pos.x, mouseY - pos.y);
        if (dist < 18) {
          found = c;
          break;
        }
      }
    }

    if (found !== hoveredCountry) {
      hoveredCountry = found;
      canvas.style.cursor = hoveredCountry ? "pointer" : "grab";
      render();
    }
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;

    // 1. Atmosphere Outer Glow Rim
    const atmoGrad = ctx.createRadialGradient(cx, cy, radius * 0.95, cx, cy, radius * 1.15);
    atmoGrad.addColorStop(0, "rgba(56, 189, 248, 0.4)");
    atmoGrad.addColorStop(0.6, "rgba(14, 165, 233, 0.15)");
    atmoGrad.addColorStop(1, "rgba(14, 165, 233, 0)");

    ctx.fillStyle = atmoGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.15, 0, Math.PI * 2);
    ctx.fill();

    // 2. Realistic Earth Ocean Base (Deep Blue Depth Gradient)
    const oceanGrad = ctx.createRadialGradient(cx - radius * 0.35, cy - radius * 0.35, radius * 0.1, cx, cy, radius);
    oceanGrad.addColorStop(0, "#1e40af");   // Deep blue specular highlight
    oceanGrad.addColorStop(0.5, "#1e3a8a");  // Royal ocean blue
    oceanGrad.addColorStop(0.85, "#0f172a"); // Deep abyssal navy
    oceanGrad.addColorStop(1, "#020617");    // Dark space limb

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fillStyle = oceanGrad;
    ctx.shadowColor = "rgba(14, 165, 233, 0.3)";
    ctx.shadowBlur = 30;
    ctx.fill();
    ctx.clip();

    // 3. Realistic Green Continents & Landmass Geometry
    for (const poly of CONTINENTS) {
      ctx.beginPath();
      let first = true;
      let visibleCount = 0;

      for (const pt of poly) {
        const pos = latLngTo3D(pt[0], pt[1]);
        if (pos.visible) {
          visibleCount++;
          if (first) { ctx.moveTo(pos.x, pos.y); first = false; }
          else { ctx.lineTo(pos.x, pos.y); }
        }
      }

      if (visibleCount > 2) {
        ctx.closePath();
        // Landfill natural green gradient
        ctx.fillStyle = "rgba(34, 197, 94, 0.75)";
        ctx.strokeStyle = "rgba(74, 222, 128, 0.9)";
        ctx.lineWidth = 1.2;
        ctx.fill();
        ctx.stroke();
      }
    }

    // 4. Lat/Lng Graticule Lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
    ctx.lineWidth = 0.8;

    for (let lat = -60; lat <= 60; lat += 30) {
      ctx.beginPath();
      let first = true;
      for (let lng = -180; lng <= 180; lng += 15) {
        const pos = latLngTo3D(lat, lng);
        if (pos.visible) {
          if (first) { ctx.moveTo(pos.x, pos.y); first = false; }
          else { ctx.lineTo(pos.x, pos.y); }
        }
      }
      ctx.stroke();
    }

    // 5. Country Markers & Glowing Pins
    for (const c of countriesData) {
      const pos = latLngTo3D(c.latitude, c.longitude);
      if (pos.visible) {
        const isHovered = hoveredCountry && hoveredCountry.id === c.id;

        // Outer pulse ring
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, isHovered ? 11 : 6, 0, Math.PI * 2);
        ctx.fillStyle = isHovered ? "rgba(244, 114, 182, 0.5)" : "rgba(250, 204, 21, 0.35)";
        ctx.fill();

        // Pin core
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, isHovered ? 6 : 3.5, 0, Math.PI * 2);
        ctx.fillStyle = isHovered ? "#f43f5e" : "#facc15";
        ctx.fill();

        // Label flag & country name
        ctx.font = isHovered ? "bold 13px sans-serif" : "10px sans-serif";
        ctx.fillStyle = isHovered ? "#ffffff" : "rgba(255, 255, 255, 0.9)";
        ctx.fillText(`${c.flag_emoji} ${c.name}`, pos.x + 8, pos.y + 4);
      }
    }

    // 6. Rich Hover Tooltip Box
    if (hoveredCountry) {
      const pos = latLngTo3D(hoveredCountry.latitude, hoveredCountry.longitude);
      if (pos.visible) {
        const line1 = `${hoveredCountry.flag_emoji} ${hoveredCountry.name}`;
        const line2 = `${hoveredCountry.destination_count} Destinations • ${hoveredCountry.continent || 'Global'}`;

        ctx.font = "bold 13px sans-serif";
        const w1 = ctx.measureText(line1).width;
        ctx.font = "11px sans-serif";
        const w2 = ctx.measureText(line2).width;
        const boxWidth = Math.max(w1, w2) + 24;

        const tx = Math.min(pos.x + 12, width - boxWidth - 10);
        const ty = Math.max(pos.y - 45, 10);

        // Tooltip container
        ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
        ctx.strokeStyle = "rgba(56, 189, 248, 0.5)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(tx, ty, boxWidth, 42, 8);
        ctx.fill();
        ctx.stroke();

        // Text lines
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 13px sans-serif";
        ctx.fillText(line1, tx + 12, ty + 18);

        ctx.fillStyle = "#38bdf8";
        ctx.font = "11px sans-serif";
        ctx.fillText(line2, tx + 12, ty + 34);
      }
    }

    ctx.restore();
  }

  // Auto slow rotation when idle
  setInterval(() => {
    if (!isDragging && !hoveredCountry) {
      rotationY += 0.002;
      render();
    }
  }, 30);
});
