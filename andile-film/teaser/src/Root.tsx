import React from 'react';
import { Composition } from 'remotion';
import { CastTeaser } from './CastTeaser';
import T from './teaser.json';
import { Scene1 } from './Scene1';
import S1 from './scene1.json';
import { TaxiRank } from './TaxiRank';
import TR from './taxirank.json';

const total = T.intro + T.cast.length * T.beat + T.outro;

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="CastTeaser" component={CastTeaser} durationInFrames={total} fps={T.fps} width={1920} height={1080} />
    <Composition id="CastTeaserVertical" component={CastTeaser} durationInFrames={total} fps={T.fps} width={1080} height={1920} />
    <Composition id="Scene1" component={Scene1} durationInFrames={S1.frames} fps={S1.fps} width={1920} height={1080} />
    <Composition id="TaxiRank" component={TaxiRank} durationInFrames={TR.frames} fps={TR.fps} width={1920} height={1080} />
  </>
);
