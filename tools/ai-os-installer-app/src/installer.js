let THREE = null;

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const root = document.documentElement;

function wait(milliseconds) {
  return new Promise(resolve => window.setTimeout(resolve, milliseconds));
}

function setBootStatus(message) {
  const status = document.querySelector(".boot-status");
  if (status) status.textContent = message;
}

function activateSetup(persist = true) {
  if (persist) sessionStorage.setItem("ai-os-setup-entered", "1");
  const content = document.querySelector(".content");
  if (content) content.scrollTop = 0;
  if (!persist || root.classList.contains("setup-active")) {
    root.classList.add("setup-active");
    window.dispatchEvent(new CustomEvent("aios:setup-active"));
    return;
  }

  root.classList.add("setup-transitioning");
  window.dispatchEvent(new CustomEvent("aios:setup-transition-start"));
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      root.classList.add("setup-active");
      window.dispatchEvent(new CustomEvent("aios:setup-active"));
      window.setTimeout(() => {
        root.classList.remove("setup-transitioning");
        window.dispatchEvent(new CustomEvent("aios:setup-transition-complete"));
      }, reducedMotion.matches ? 0 : 1120);
    });
  });
}

function revealIntro() {
  root.classList.add("boot-complete");
  window.dispatchEvent(new CustomEvent("aios:boot-complete"));
}

function bindExperience() {
  const entry = Boolean(document.querySelector("[data-installer-entry]"));
  const alreadyEntered = sessionStorage.getItem("ai-os-setup-entered") === "1";
  const begin = document.getElementById("begin-setup");
  const skip = document.querySelector(".boot-skip");

  if (!entry || alreadyEntered) {
    activateSetup(false);
    revealIntro();
  }
  if (begin) begin.addEventListener("click", () => activateSetup(true));
  if (skip) skip.addEventListener("click", revealIntro);
  return { entry, alreadyEntered, firstEntry: entry && !alreadyEntered };
}

function updateRailPhase() {
  const heading = document.querySelector(".content h1")?.textContent?.trim() || "";
  let phase = 1;
  if (heading.includes("Собираем")) phase = 2;
  if (heading.toLowerCase().includes("готов") || heading.includes("Нужна проверка")) phase = 3;

  const copy = {
    1: {
      kicker: "Проект · 01",
      title: "Параметры проекта",
      text: "У каждого проекта будет своя папка с заметками, правилами и памятью.",
    },
    2: {
      kicker: "Установка · 02",
      title: "Устанавливаем недостающее",
      text: "Общие компоненты загрузятся один раз и останутся в локальном кэше.",
    },
    3: {
      kicker: "Готово · 03",
      title: "Проект готов",
      text: "Можно открыть AI OS или папку проекта.",
    },
  }[phase];

  root.dataset.phase = String(phase);
  const kicker = document.querySelector("[data-phase-kicker]");
  const title = document.querySelector("[data-phase-title]");
  const text = document.querySelector("[data-phase-copy]");
  if (kicker) kicker.textContent = copy.kicker;
  if (title) title.textContent = copy.title;
  if (text) text.textContent = copy.text;
  document.querySelectorAll(".steps li").forEach((step, index) => {
    step.classList.toggle("active", index === phase - 1);
    if (index === phase - 1) step.setAttribute("aria-current", "step");
    else step.removeAttribute("aria-current");
  });
}

function bindWindowChrome() {
  const request = action => fetch("/window/" + action, { cache: "no-store" }).catch(() => {});
  document.querySelectorAll("[data-window-action]").forEach(button => {
    button.addEventListener("click", event => {
      event.preventDefault();
      event.stopPropagation();
      request(button.dataset.windowAction);
    });
  });
  const titlebar = document.querySelector("[data-window-drag]");
  if (titlebar) {
    titlebar.addEventListener("pointerdown", event => {
      if (event.button === 0 && !event.target.closest("[data-window-action]")) request("drag");
    });
    titlebar.addEventListener("dblclick", event => {
      if (!event.target.closest("[data-window-action]")) request("maximize");
    });
  }
}

function bindInteractions() {
  document.querySelectorAll("details.workspace").forEach(item => {
    item.addEventListener("toggle", () => item.classList.toggle("is-open", item.open));
  });
  document.querySelectorAll('form[action="/install"]').forEach(form => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (!button) return;
      button.disabled = true;
      button.classList.add("is-loading");
      button.innerHTML = '<span class="loader" aria-hidden="true"></span> Подготавливаем';
    });
  });
}

function seededRandom(seed) {
  return () => {
    seed |= 0;
    seed = seed + 0x6D2B79F5 | 0;
    let value = Math.imul(seed ^ seed >>> 15, 1 | seed);
    value = value + Math.imul(value ^ value >>> 7, 61 | value) ^ value;
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
}

function typedAccessor(document, binary, accessorIndex) {
  const accessor = document.accessors[accessorIndex];
  const bufferView = document.bufferViews[accessor.bufferView];
  const components = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 }[accessor.type];
  const constructors = {
    5121: Uint8Array,
    5123: Uint16Array,
    5125: Uint32Array,
    5126: Float32Array,
  };
  const Constructor = constructors[accessor.componentType];
  if (!components || !Constructor || bufferView.byteStride) throw new Error("Unsupported brain mesh layout");
  const byteOffset = binary.byteOffset + (bufferView.byteOffset || 0) + (accessor.byteOffset || 0);
  return new Constructor(binary.buffer, byteOffset, accessor.count * components);
}

async function loadBrainSurface() {
  const response = await fetch("/assets/brain.glb", { cache: "force-cache" });
  if (!response.ok) throw new Error(`Brain mesh unavailable (${response.status})`);
  const data = await response.arrayBuffer();
  const header = new DataView(data);
  if (header.getUint32(0, true) !== 0x46546c67 || header.getUint32(4, true) !== 2) {
    throw new Error("Invalid brain mesh");
  }
  let offset = 12;
  let document;
  let binary;
  while (offset < data.byteLength) {
    const length = header.getUint32(offset, true);
    const type = header.getUint32(offset + 4, true);
    offset += 8;
    if (type === 0x4e4f534a) {
      const json = new TextDecoder().decode(new Uint8Array(data, offset, length)).replace(/[\u0000 ]+$/g, "");
      document = JSON.parse(json);
    } else if (type === 0x004e4942) {
      binary = new Uint8Array(data, offset, length);
    }
    offset += length;
  }
  if (!document || !binary) throw new Error("Incomplete brain mesh");
  const primitive = document.meshes[0].primitives[0];
  return {
    positions: typedAccessor(document, binary, primitive.attributes.POSITION),
    indices: typedAccessor(document, binary, primitive.indices),
  };
}

function sampledBrainSurface(positions, indices, count, rand) {
  const cumulative = new Float64Array(indices.length / 3);
  const a = new THREE.Vector3();
  const b = new THREE.Vector3();
  const c = new THREE.Vector3();
  const ab = new THREE.Vector3();
  const ac = new THREE.Vector3();
  let totalArea = 0;
  for (let triangle = 0; triangle < cumulative.length; triangle += 1) {
    a.fromArray(positions, indices[triangle * 3] * 3);
    b.fromArray(positions, indices[triangle * 3 + 1] * 3);
    c.fromArray(positions, indices[triangle * 3 + 2] * 3);
    totalArea += ab.subVectors(b, a).cross(ac.subVectors(c, a)).length() * 0.5;
    cumulative[triangle] = totalArea;
  }
  const points = new Array(count);
  const normals = new Array(count);
  for (let sample = 0; sample < count; sample += 1) {
    const target = rand() * totalArea;
    let low = 0;
    let high = cumulative.length - 1;
    while (low < high) {
      const middle = (low + high) >>> 1;
      if (cumulative[middle] < target) low = middle + 1;
      else high = middle;
    }
    a.fromArray(positions, indices[low * 3] * 3);
    b.fromArray(positions, indices[low * 3 + 1] * 3);
    c.fromArray(positions, indices[low * 3 + 2] * 3);
    let u = rand();
    let v = rand();
    if (u + v > 1) {
      u = 1 - u;
      v = 1 - v;
    }
    const point = a.clone().addScaledVector(ab.subVectors(b, a), u).addScaledVector(ac.subVectors(c, a), v);
    const normal = ab.subVectors(b, a).cross(ac.subVectors(c, a)).normalize().clone();
    points[sample] = point;
    normals[sample] = normal;
  }
  return { points, normals };
}

const BRAIN_PALETTE = [
  "#f7f4ed",
  "#f5b720",
  "#7652ff",
  "#15a68d",
  "#34d8ef",
  "#ed66a4",
];

const COLOR_REGIONS = [
  [-0.54, 0.30, 0.18, 2], [-0.35, 0.35, 0.38, 0], [-0.09, 0.40, 0.28, 1],
  [0.19, 0.37, 0.34, 0], [0.43, 0.30, 0.15, 1], [0.57, 0.05, 0.27, 0],
  [0.48, -0.24, 0.34, 1], [0.20, -0.31, 0.46, 2], [-0.08, -0.33, 0.46, 3],
  [-0.37, -0.28, 0.34, 0], [-0.59, -0.04, 0.27, 3], [-0.29, 0.08, 0.46, 0],
  [-0.24, 0.34, -0.37, 4], [0.04, 0.30, -0.43, 0], [0.27, 0.22, -0.42, 5],
  [0.52, 0.03, -0.31, 1], [0.31, -0.25, -0.34, 2], [0.02, -0.26, -0.41, 3],
  [-0.36, -0.21, -0.34, 2], [-0.51, 0.11, -0.27, 0], [0.02, 0.04, 0.05, 0],
];

function regionColor(point, normal, rand) {
  let best = COLOR_REGIONS[0];
  let bestDistance = Infinity;
  for (const region of COLOR_REGIONS) {
    const dx = point.x - region[0];
    const dy = point.y - region[1];
    const dz = (point.z - region[2]) * 0.78;
    const distance = dx * dx + dy * dy + dz * dz;
    if (distance < bestDistance) {
      best = region;
      bestDistance = distance;
    }
  }
  let colorIndex = best[3];
  const seam = Math.sin(point.x * 17 + point.y * 11 - point.z * 7) + Math.cos(point.y * 19 + point.z * 9);
  if (seam > 1.25 && rand() > 0.33) colorIndex = 0;
  else if (rand() > 0.965) colorIndex = 4 + Math.floor(rand() * 2);
  const front = THREE.MathUtils.clamp((point.z + 0.53) / 1.06, 0, 1);
  const light = 0.52 + front * 0.18 + Math.max(0, normal.z) * 0.20 + rand() * 0.12;
  return new THREE.Color(BRAIN_PALETTE[colorIndex]).multiplyScalar(light);
}

const BRAIN_VERTEX_SHADER = `
  attribute float instanceSeed;
  attribute vec3 instanceDrift;
  uniform float uTime;
  uniform vec3 uPointer;
  uniform float uPointerActive;
  uniform float uLayerScale;
  uniform float uReveal;
  uniform float uDisperse;
  varying vec3 vColor;
  varying float vReveal;
  varying float vDisperse;
  mat2 rotate2d(float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return mat2(c, -s, s, c);
  }
  void main() {
    vec3 origin = (instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
    float proximity = smoothstep(0.32, 0.035, distance(origin.xy, uPointer.xy)) * uPointerActive;
    float idle = sin(uTime * 0.42 + instanceSeed * 11.0) * 0.018;
    float reveal = smoothstep(instanceSeed * 0.42, 0.58 + instanceSeed * 0.42, uReveal);
    float disperse = smoothstep(instanceSeed * 0.48, 0.34 + instanceSeed * 0.66, uDisperse);
    float angle = instanceSeed * 6.28318 + proximity * (0.6 + instanceSeed) + uTime * 0.012;
    vec3 local = position * uLayerScale * reveal * (1.0 + idle + proximity * 0.72) * (1.0 - disperse * 0.16);
    local.xy = rotate2d(angle * 0.38) * local.xy;
    local.xz = rotate2d(angle * 0.22) * local.xz;
    vec4 world = instanceMatrix * vec4(local, 1.0);
    vec3 assembleDrift = instanceDrift * (1.0 - reveal) * (0.42 + instanceSeed * 0.46);
    float release = pow(disperse, 1.45);
    vec3 scrollDrift = instanceDrift * disperse * (0.18 + release * 4.65);
    float curl = sin(instanceSeed * 31.0 + uTime * 0.16) * release;
    float side = origin.x < 0.0 ? -1.0 : 1.0;
    scrollDrift += vec3(
      side * release * (0.22 + instanceSeed * 0.56) + curl * 0.18,
      sin(instanceSeed * 27.0) * release * 0.92,
      cos(instanceSeed * 19.0) * release * 0.44
    );
    world.xyz += assembleDrift + scrollDrift;
    gl_Position = projectionMatrix * modelViewMatrix * world;
    vColor = instanceColor * (1.0 + proximity * 0.18 + disperse * 0.08);
    vReveal = reveal;
    vDisperse = disperse;
  }
`;

const BRAIN_FRAGMENT_SHADER = `
  uniform float uOpacity;
  varying vec3 vColor;
  varying float vReveal;
  varying float vDisperse;
  void main() {
    gl_FragColor = vec4(vColor, uOpacity * vReveal * (1.0 - vDisperse * 0.88));
  }
`;

const BRAIN_SURFACE_VERTEX_SHADER = `
  uniform float uReveal;
  uniform float uDisperse;
  varying vec3 vNormalView;
  varying vec3 vViewPosition;
  varying float vAlpha;
  void main() {
    float reveal = smoothstep(0.02, 0.72, uReveal);
    vec3 transformed = position * mix(0.965, 1.0, reveal);
    vec4 viewPosition = modelViewMatrix * vec4(transformed, 1.0);
    vNormalView = normalize(normalMatrix * normal);
    vViewPosition = viewPosition.xyz;
    vAlpha = reveal * pow(1.0 - uDisperse, 1.7);
    gl_Position = projectionMatrix * viewPosition;
  }
`;

const BRAIN_SURFACE_FRAGMENT_SHADER = `
  varying vec3 vNormalView;
  varying vec3 vViewPosition;
  varying float vAlpha;
  void main() {
    vec3 viewDirection = normalize(-vViewPosition);
    float facing = max(dot(normalize(vNormalView), viewDirection), 0.0);
    float fresnel = pow(1.0 - facing, 2.35);
    vec3 deep = vec3(0.004, 0.006, 0.018);
    vec3 rim = vec3(0.08, 0.12, 0.42);
    vec3 color = mix(deep, rim, fresnel);
    float alpha = (0.004 + fresnel * 0.060) * vAlpha;
    gl_FragColor = vec4(color, alpha);
  }
`;

function createTriangleFrameGeometry(radius = 0.0048, inset = 0.54) {
  const positions = [];
  for (const scale of [1, inset]) {
    for (let corner = 0; corner < 3; corner += 1) {
      const angle = Math.PI * 0.5 + corner * Math.PI * 2 / 3;
      positions.push(Math.cos(angle) * radius * scale, 0, Math.sin(angle) * radius * scale);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex([
    0, 1, 4, 0, 4, 3,
    1, 2, 5, 1, 5, 4,
    2, 0, 3, 2, 3, 5,
  ]);
  geometry.computeVertexNormals();
  return geometry;
}

async function createBrain() {
  const source = await loadBrainSurface();
  const rand = seededRandom(0xA1052026);
  const cores = navigator.hardwareConcurrency || 8;
  const count = cores <= 4 ? 14000 : cores <= 8 ? 22000 : 32000;
  const sampled = sampledBrainSurface(source.positions, source.indices, count, rand);
  const geometry = createTriangleFrameGeometry();
  const instanceSeeds = Float32Array.from({ length: count }, () => rand());
  const instanceDrifts = new Float32Array(count * 3);
  geometry.setAttribute("instanceSeed", new THREE.InstancedBufferAttribute(instanceSeeds, 1));
  const sharedUniforms = {
    uTime: { value: 0 },
    uPointer: { value: new THREE.Vector3(9, 9, 0) },
    uPointerActive: { value: 0 },
    uReveal: { value: 0 },
    uDisperse: { value: 0 },
  };
  const material = new THREE.ShaderMaterial({
    uniforms: {
      ...sharedUniforms,
      uLayerScale: { value: 1 },
      uOpacity: { value: 0.86 },
    },
    vertexShader: BRAIN_VERTEX_SHADER,
    fragmentShader: BRAIN_FRAGMENT_SHADER,
    side: THREE.DoubleSide,
    transparent: true,
    depthWrite: true,
  });
  const glowMaterial = new THREE.ShaderMaterial({
    uniforms: {
      ...sharedUniforms,
      uLayerScale: { value: 1.42 },
      uOpacity: { value: 0.018 },
    },
    vertexShader: BRAIN_VERTEX_SHADER,
    fragmentShader: BRAIN_FRAGMENT_SHADER,
    side: THREE.DoubleSide,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const mesh = new THREE.InstancedMesh(geometry, material, count);
  const glow = new THREE.InstancedMesh(geometry, glowMaterial, count);
  const dummy = new THREE.Object3D();
  const up = new THREE.Vector3(0, 1, 0);
  const spin = new THREE.Quaternion();
  const outward = new THREE.Vector3();
  const drift = new THREE.Vector3();
  for (let i = 0; i < count; i += 1) {
    const point = sampled.points[i];
    const normal = sampled.normals[i];
    dummy.position.copy(point);
    dummy.quaternion.setFromUnitVectors(up, normal);
    spin.setFromAxisAngle(normal, rand() * Math.PI * 2);
    dummy.quaternion.premultiply(spin);
    const scale = 0.48 + Math.pow(rand(), 0.72) * 1.22;
    dummy.scale.setScalar(scale);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
    glow.setMatrixAt(i, dummy.matrix);
    const color = regionColor(point, normal, rand);
    mesh.setColorAt(i, color);
    glow.setColorAt(i, color);
    outward.copy(point).normalize();
    drift.set(rand() - 0.5, rand() - 0.42, (rand() - 0.5) * 0.72).normalize();
    drift.multiplyScalar(0.28 + rand() * 0.54);
    drift.addScaledVector(outward, 0.34 + rand() * 0.42);
    drift.addScaledVector(normal, 0.10 + rand() * 0.26);
    instanceDrifts[i * 3] = drift.x;
    instanceDrifts[i * 3 + 1] = drift.y;
    instanceDrifts[i * 3 + 2] = drift.z;
  }
  geometry.setAttribute("instanceDrift", new THREE.InstancedBufferAttribute(instanceDrifts, 3));
  mesh.instanceMatrix.needsUpdate = true;
  glow.instanceMatrix.needsUpdate = true;
  mesh.instanceColor.needsUpdate = true;
  glow.instanceColor.needsUpdate = true;
  mesh.frustumCulled = false;
  glow.frustumCulled = false;

  const sourceGeometry = new THREE.BufferGeometry();
  sourceGeometry.setAttribute("position", new THREE.BufferAttribute(source.positions, 3));
  sourceGeometry.setIndex(new THREE.BufferAttribute(source.indices, 1));
  sourceGeometry.computeVertexNormals();
  sourceGeometry.computeBoundingBox();
  const modelCenter = sourceGeometry.boundingBox.getCenter(new THREE.Vector3());
  const surface = new THREE.Mesh(
    sourceGeometry,
    new THREE.ShaderMaterial({
      uniforms: sharedUniforms,
      vertexShader: BRAIN_SURFACE_VERTEX_SHADER,
      fragmentShader: BRAIN_SURFACE_FRAGMENT_SHADER,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    }),
  );
  const picker = new THREE.Mesh(
    sourceGeometry,
    new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, transparent: true, opacity: 0 }),
  );

  const model = new THREE.Group();
  model.scale.setScalar(2.55);
  model.position.copy(modelCenter).multiplyScalar(-1);
  model.add(surface, glow, mesh, picker);
  const group = new THREE.Group();
  group.add(model);
  group.position.set(-0.04, 0.39, 0);
  group.rotation.set(-0.02, -0.06, -0.018);
  return { group, model, surface, mesh, glow, picker, uniforms: sharedUniforms };
}

function createDust() {
  const count = 420;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const palette = ["#8052ff", "#ffb829", "#15846e", "#3dd6f5"];
  for (let i = 0; i < count; i += 1) {
    const radius = 3.4 + Math.random() * 4.2;
    const angle = Math.random() * Math.PI * 2;
    positions[i * 3] = Math.cos(angle) * radius;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 7.2;
    positions[i * 3 + 2] = Math.sin(angle) * radius - 1.4;
    const color = new THREE.Color(palette[i % palette.length]).multiplyScalar(0.42);
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  return new THREE.Points(
    geometry,
    new THREE.PointsMaterial({
      size: 0.9,
      sizeAttenuation: false,
      vertexColors: true,
      transparent: true,
      opacity: 0.34,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
}

async function startScene() {
  const canvas = document.getElementById("knowledge-field");
  if (!canvas) return;
  try {
    THREE = await import("./three.module.min.js");
    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
      preserveDrawingBuffer: false,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0.08, 6.55);
    const brain = await createBrain();
    const dust = createDust();
    scene.add(brain.group, dust);
    document.documentElement.classList.add("webgl-ready");

    const pointer = new THREE.Vector2();
    const target = new THREE.Vector2();
    const brainPointer = new THREE.Vector3(9, 9, 0);
    const brainPointerTarget = new THREE.Vector3(9, 9, 0);
    const raycaster = new THREE.Raycaster();
    let pointerActive = 0;
    let pointerActiveTarget = 0;
    const start = performance.now();
    let revealProgress = 0;
    let layoutProgress = root.classList.contains("setup-active") ? 1 : 0;
    let visible = true;
    let layoutTransition = false;
    let retired = false;
    let resizeFrame = 0;
    let resizePending = false;

    function render(now) {
      if (retired) return;
      const elapsed = (now - start) / 1000;
      target.lerp(pointer, 0.035);
      brainPointer.lerp(brainPointerTarget, 0.12);
      pointerActive += (pointerActiveTarget - pointerActive) * 0.11;
      const revealTarget = root.classList.contains("boot-complete") ? 1 : 0;
      const layoutTarget = root.classList.contains("setup-active") ? 1 : 0;
      revealProgress += (revealTarget - revealProgress) * (reducedMotion.matches ? 1 : 0.045);
      layoutProgress += (layoutTarget - layoutProgress) * (reducedMotion.matches ? 1 : 0.055);
      const revealEase = 1 - Math.pow(1 - revealProgress, 4);
      const layoutEase = layoutProgress * layoutProgress * (3 - 2 * layoutProgress);
      const sceneScale = THREE.MathUtils.lerp(1.08, 1.0, layoutEase);
      brain.group.scale.setScalar((0.76 + revealEase * 0.24 + Math.sin(elapsed * 0.32) * 0.0025) * sceneScale);
      brain.group.position.x = THREE.MathUtils.lerp(0.68, -0.04, layoutEase);
      brain.group.position.y = THREE.MathUtils.lerp(0.25, 0.39, layoutEase);
      brain.group.rotation.y = -0.06 + target.x * 0.085 + Math.sin(elapsed * 0.12) * 0.004;
      brain.group.rotation.x = -0.02 - target.y * 0.042 + Math.sin(elapsed * 0.17) * 0.003;
      brain.group.rotation.z = -0.018 + target.x * 0.008;
      camera.position.z = THREE.MathUtils.lerp(6.18, 6.55, layoutEase);
      brain.uniforms.uTime.value = elapsed;
      brain.uniforms.uPointer.value.copy(brainPointer);
      brain.uniforms.uPointerActive.value = pointerActive;
      brain.uniforms.uReveal.value = revealEase;
      brain.uniforms.uDisperse.value = 0;
      brain.glow.material.uniforms.uOpacity.value = 0.024 + (Math.sin(elapsed * 0.48) + 1) * 0.008;
      dust.material.opacity = THREE.MathUtils.lerp(0.38, 0.26, layoutEase) * revealEase;
      dust.rotation.y = -elapsed * 0.006;
      dust.rotation.z = Math.sin(elapsed * 0.09) * 0.018;
      renderer.render(scene, camera);
    }

    function loop(now) {
      render(now);
    }

    function updateMotion() {
      renderer.setAnimationLoop(null);
      if (retired) return;
      if (reducedMotion.matches || !visible || layoutTransition) render(performance.now());
      else renderer.setAnimationLoop(loop);
    }

    function resize() {
      if (layoutTransition) {
        resizePending = true;
        return;
      }
      const rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      renderer.setSize(rect.width, rect.height, false);
      camera.aspect = rect.width / rect.height;
      camera.updateProjectionMatrix();
      render(performance.now());
    }

    function scheduleResize() {
      if (layoutTransition) {
        resizePending = true;
        return;
      }
      if (resizeFrame) return;
      resizeFrame = window.requestAnimationFrame(() => {
        resizeFrame = 0;
        resize();
      });
    }

    window.addEventListener("pointermove", event => {
      const rect = canvas.getBoundingClientRect();
      const x = (event.clientX - rect.left) / Math.max(1, rect.width);
      const y = (event.clientY - rect.top) / Math.max(1, rect.height);
      pointer.set(x * 2 - 1, -(y * 2 - 1));
      if (x < 0 || x > 1 || y < 0 || y > 1) {
        pointerActiveTarget = 0;
        return;
      }
      camera.updateMatrixWorld();
      brain.group.updateMatrixWorld(true);
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObject(brain.picker, false)[0];
      if (hit) {
        brainPointerTarget.copy(brain.picker.worldToLocal(hit.point.clone()));
        pointerActiveTarget = 1;
      } else {
        pointerActiveTarget = 0;
      }
    }, { passive: true });
    window.addEventListener("pointerleave", () => {
      pointer.set(0, 0);
      pointerActiveTarget = 0;
    });
    document.addEventListener("visibilitychange", () => {
      visible = !document.hidden;
      updateMotion();
    });
    const renderStaticState = () => {
      if (reducedMotion.matches) window.requestAnimationFrame(render);
    };
    window.addEventListener("aios:boot-complete", renderStaticState);
    window.addEventListener("aios:setup-active", () => {
      renderStaticState();
    });
    window.addEventListener("aios:setup-transition-start", () => {
      layoutTransition = true;
      resizePending = false;
      renderer.setAnimationLoop(null);
      render(performance.now());
    });
    window.addEventListener("aios:setup-transition-complete", () => {
      layoutTransition = false;
      resizePending = false;
      retired = true;
      renderer.setAnimationLoop(null);
      scene.traverse(object => {
        object.geometry?.dispose?.();
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.filter(Boolean).forEach(material => material.dispose?.());
      });
      renderer.dispose();
      canvas.width = 1;
      canvas.height = 1;
      root.classList.add("scene-retired");
    });
    reducedMotion.addEventListener("change", () => {
      updateMotion();
    });
    new ResizeObserver(scheduleResize).observe(canvas);
    resize();
    updateMotion();
  } catch (error) {
    console.warn("AI OS visual scene is unavailable", error);
  }
}

bindWindowChrome();
bindInteractions();
updateRailPhase();
const experience = bindExperience();
const fontReady = document.fonts?.ready.then(() => setBootStatus("Загружаем интерфейс")) ?? Promise.resolve();
const sceneReady = experience.firstEntry
  ? startScene().then(() => setBootStatus("Готовим изображение"))
  : Promise.resolve();
if (experience.entry && !experience.alreadyEntered) {
  const minimum = reducedMotion.matches ? 120 : 1050;
  Promise.allSettled([fontReady, sceneReady, wait(minimum)]).then(() => {
    setBootStatus("Всё готово");
    window.setTimeout(revealIntro, reducedMotion.matches ? 0 : 180);
  });
}
