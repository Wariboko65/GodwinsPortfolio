import React from "react";
import { Composition } from "remotion";
import { WasteChart } from "./WasteChart";

export const Root: React.FC = () => (
  <Composition id="WasteChart" component={WasteChart} durationInFrames={462} fps={30} width={1920} height={1080} />
);
