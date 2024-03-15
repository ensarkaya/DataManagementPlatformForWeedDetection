const wktToLeafletCoords = (wktString: string): [number, number][] => {
  const regex = /\d+\.\d+\s\d+\.\d+/g;
  const matches = wktString.match(regex) || [];

  return matches.map((match) => {
    const [lon, lat] = match.split(" ").map(parseFloat);
    return [lat, lon];
  });
};
const wktToCoords = (wktString: string): { lat: number; lng: number }[] => {
  const regex = /\d+\.\d+\s\d+\.\d+/g;
  const matches = wktString.match(regex) || [];

  return matches.map((match) => {
    const [lon, lat] = match.split(" ").map(parseFloat);
    return { lat, lng: lon };
  });
};

export { wktToLeafletCoords, wktToCoords };
