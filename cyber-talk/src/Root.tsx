import "./index.css";
import { Composition } from "remotion";
import { CyberTalk } from "./CyberTalk";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CyberSecurityTalk"
      component={CyberTalk}
      durationInFrames={900}
      fps={30}
      width={1280}
      height={720}
    />
  );
};
