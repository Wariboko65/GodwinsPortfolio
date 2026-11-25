import React from "react";
import { Composition } from "remotion";
import { WasteChart } from "./WasteChart";
import { Bottles } from "./Bottles";

export const Root: React.FC = () => (
  <>
  <Composition id="Bottles" component={Bottles} durationInFrames={174} fps={30} width={1080} height={1080} />
  <Composition id="WasteChart" component={WasteChart} durationInFrames={462} fps={30} width={1920} height={1080} />
  </>
);
