import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Img,
  staticFile,
} from "remotion";
import React from "react";

// Each scene lasts 5 seconds at 30fps
const SCENE_DURATION = 150;

type Scene = {
  subtitle: string;
  title: string;
  tip: string;
  color: string;
  // sprite grid position in the 1024×1536 sprite sheet (3 cols × 4 rows)
  col: number;
  row: number;
};

const SCENES: Scene[] = [
  {
    subtitle: "Welcome",
    title: "Cyber Security",
    tip: "Let me guide you through\nthe most important tips\nto stay safe online 🌐",
    color: "#00d4ff",
    col: 0,
    row: 0, // pointing-up character
  },
  {
    subtitle: "Tip #1",
    title: "🔐 Strong Passwords",
    tip: "Use 12+ characters\nMix UPPER, lower, numbers\n& symbols!\n❌ password123\n✅ P@ssw0rd#2024",
    color: "#22c55e",
    col: 1,
    row: 0, // thumbs-up character
  },
  {
    subtitle: "Tip #2",
    title: "📱 Two-Factor Auth",
    tip: "Enable 2FA on every account!\nEven if your password leaks,\nhackers can't get in 🛡️\nUse an authenticator app.",
    color: "#a855f7",
    col: 1,
    row: 1, // laptop character
  },
  {
    subtitle: "Tip #3",
    title: "⚠️ Phishing Attacks",
    tip: "Think before you click!\nAlways verify sender emails.\nReal companies NEVER ask\nfor passwords via email!",
    color: "#ef4444",
    col: 0,
    row: 2, // sunglasses/alert character
  },
  {
    subtitle: "Tip #4",
    title: "🔄 Stay Updated",
    tip: "Keep all software updated!\nUpdates patch vulnerabilities\nthat hackers actively exploit.\nEnable auto-updates ✅",
    color: "#f59e0b",
    col: 2,
    row: 0, // tablet character
  },
  {
    subtitle: "You're Ready!",
    title: "🏆 Cyber Champion",
    tip: "You now know the essentials\nof Cyber Security!\nStay alert, stay updated,\nand stay safe! 💪",
    color: "#00d4ff",
    col: 1,
    row: 0, // thumbs-up to celebrate
  },
];

// Sprite sheet dimensions: 1024×1536, 3 cols × ~4 rows
// Cell size: ~341×384px
const CELL_W = 341;
const CELL_H = 384;
// Display scale so one cell fills ~400px tall panel
const SPRITE_SCALE = 1.66; // 384 * 1.66 ≈ 638px

function GridLines() {
  const lines = [];
  for (let i = 0; i < 8; i++) {
    lines.push(
      <div
        key={`h${i}`}
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: `${(i + 1) * 12.5}%`,
          height: 1,
          background: "rgba(0,212,255,0.05)",
        }}
      />,
      <div
        key={`v${i}`}
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: `${(i + 1) * 12.5}%`,
          width: 1,
          background: "rgba(0,212,255,0.05)",
        }}
      />
    );
  }
  return <>{lines}</>;
}

function ScanLine({ frame }: { frame: number }) {
  const y = (frame * 4) % 800;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: y,
        height: 60,
        background:
          "linear-gradient(to bottom, transparent, rgba(0,212,255,0.03), transparent)",
        pointerEvents: "none",
      }}
    />
  );
}

type CharacterProps = {
  frame: number;
  sceneIndex: number;
  localFrame: number;
};

function Character({ frame, sceneIndex, localFrame }: CharacterProps) {
  const scene = SCENES[sceneIndex];

  // Gentle bob
  const bob = Math.sin(frame * 0.07) * 7;
  // Subtle talking pulse on scale
  const talkScale = 1 + Math.sin(frame * 0.22) * 0.01;
  // Entry bounce on scene change
  const entryY = interpolate(localFrame, [0, 25], [50, 0], {
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const entryOpacity = interpolate(localFrame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Compute which portion of sprite sheet to show
  const scaledW = 1024 * SPRITE_SCALE;
  const scaledH = 1536 * SPRITE_SCALE;
  const cellW = CELL_W * SPRITE_SCALE;
  const cellH = CELL_H * SPRITE_SCALE;

  // Container shows one cell: ~566×638px
  const containerW = Math.round(cellW);
  const containerH = Math.round(cellH);

  const imgLeft = -(scene.col * cellW);
  const imgTop = -(scene.row * cellH);

  return (
    <div
      style={{
        position: "absolute",
        right: 40,
        bottom: 60,
        width: containerW,
        height: containerH,
        overflow: "hidden",
        transform: `translateY(${bob + entryY}px) scale(${talkScale})`,
        opacity: entryOpacity,
        transformOrigin: "bottom center",
      }}
    >
      <Img
        src={staticFile("character.png")}
        style={{
          position: "absolute",
          width: scaledW,
          height: scaledH,
          left: imgLeft,
          top: imgTop,
          userSelect: "none",
        }}
      />
    </div>
  );
}

type SceneContentProps = {
  scene: Scene;
};

function SceneContent({ scene }: SceneContentProps) {
  const frame = useCurrentFrame();

  const enterProgress = interpolate(frame, [0, 35], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(enterProgress, [0, 1], [50, 0]);
  const bubbleOpacity = interpolate(frame, [25, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const bubbleY = interpolate(frame, [25, 55], [20, 0], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Typewriter effect
  const charCount = Math.floor(
    interpolate(frame, [40, SCENE_DURATION - 15], [0, scene.tip.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );
  const displayedTip = scene.tip.slice(0, charCount);
  const showCursor = charCount < scene.tip.length;
  const cursorVisible = Math.floor(frame / 7) % 2 === 0;

  // Exit fade
  const exitFade = interpolate(
    frame,
    [SCENE_DURATION - 20, SCENE_DURATION - 5],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: "58%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "40px 30px 40px 70px",
        gap: 18,
        opacity: exitFade,
      }}
    >
      {/* Subtitle badge */}
      <div
        style={{
          opacity: enterProgress,
          transform: `translateY(${titleY}px)`,
          alignSelf: "flex-start",
        }}
      >
        <div
          style={{
            background: `${scene.color}22`,
            border: `2px solid ${scene.color}88`,
            borderRadius: 6,
            padding: "4px 18px",
            fontSize: 20,
            color: scene.color,
            fontWeight: 700,
            letterSpacing: 2,
            textTransform: "uppercase",
            fontFamily: "system-ui",
          }}
        >
          {scene.subtitle}
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: enterProgress,
          transform: `translateY(${titleY * 0.6}px)`,
          fontSize: 58,
          fontWeight: 900,
          color: "#ffffff",
          lineHeight: 1.1,
          fontFamily: "system-ui",
          textShadow: `0 0 40px ${scene.color}66`,
        }}
      >
        {scene.title}
      </div>

      {/* Accent line */}
      <div
        style={{
          opacity: enterProgress,
          height: 4,
          width: interpolate(enterProgress, [0, 1], [0, 220]),
          background: `linear-gradient(90deg, ${scene.color}, transparent)`,
          borderRadius: 2,
        }}
      />

      {/* Speech bubble / tip */}
      <div
        style={{
          opacity: bubbleOpacity,
          transform: `translateY(${bubbleY}px)`,
          background: "rgba(255,255,255,0.04)",
          border: `1px solid ${scene.color}33`,
          borderLeft: `4px solid ${scene.color}`,
          borderRadius: 16,
          padding: "22px 28px",
          position: "relative",
        }}
      >
        <div
          style={{
            fontSize: 24,
            color: "#e2e8f0",
            lineHeight: 1.7,
            whiteSpace: "pre-line",
            fontFamily: "system-ui, sans-serif",
          }}
        >
          {displayedTip}
          {showCursor && (
            <span
              style={{
                display: "inline-block",
                width: 2,
                height: "1em",
                background: scene.color,
                marginLeft: 3,
                verticalAlign: "text-bottom",
                opacity: cursorVisible ? 1 : 0,
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

function ProgressDots({ sceneIndex }: { sceneIndex: number }) {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 30,
        left: 0,
        width: "58%",
        display: "flex",
        justifyContent: "center",
        gap: 10,
      }}
    >
      {SCENES.map((_, i) => (
        <div
          key={i}
          style={{
            width: i === sceneIndex ? 28 : 10,
            height: 10,
            borderRadius: 5,
            background:
              i === sceneIndex
                ? SCENES[sceneIndex].color
                : "rgba(255,255,255,0.2)",
            transition: "none",
          }}
        />
      ))}
    </div>
  );
}

function TopBar({ frame }: { frame: number }) {
  const totalFrames = SCENES.length * SCENE_DURATION;
  const progress = frame / totalFrames;
  const barWidth = interpolate(progress, [0, 1], [0, 100]);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        background: "rgba(255,255,255,0.1)",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${barWidth}%`,
          background: `linear-gradient(90deg, #00d4ff, #a855f7)`,
        }}
      />
    </div>
  );
}

export const CyberTalk: React.FC = () => {
  const frame = useCurrentFrame();
  const sceneIndex = Math.min(
    Math.floor(frame / SCENE_DURATION),
    SCENES.length - 1
  );
  const localFrame = frame - sceneIndex * SCENE_DURATION;

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #060b18 0%, #0d1530 50%, #07101f 100%)",
        fontFamily: "system-ui, -apple-system, sans-serif",
        overflow: "hidden",
      }}
    >
      <GridLines />
      <ScanLine frame={frame} />

      {/* Glowing orb behind character */}
      <div
        style={{
          position: "absolute",
          right: 80,
          bottom: 80,
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${SCENES[sceneIndex].color}18 0%, transparent 70%)`,
        }}
      />

      {/* Scene content (left panel), one Sequence per scene */}
      {SCENES.map((scene, i) => (
        <Sequence
          key={i}
          from={i * SCENE_DURATION}
          durationInFrames={SCENE_DURATION}
          layout="none"
        >
          <SceneContent scene={scene} />
        </Sequence>
      ))}

      {/* Character — continuous, outside sequences */}
      <Character
        frame={frame}
        sceneIndex={sceneIndex}
        localFrame={localFrame}
      />

      <ProgressDots sceneIndex={sceneIndex} />
      <TopBar frame={frame} />
    </AbsoluteFill>
  );
};
