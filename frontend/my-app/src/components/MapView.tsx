import { LatLngTuple } from "leaflet";
import { useState } from "react";
import { MapContainer, TileLayer, FeatureGroup } from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import { tile_layer_url } from "../api/endpoints/endpoints";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

const MapView: React.FC = () => {
  const [startPosition, setStartPosition] = useState<LatLngTuple>([
    40.0672, 33.34489,
  ]);
  const [zoom, setZoom] = useState<number>(13.5);

  const handleCreated = (e: any) => {
    const { layerType, layer } = e;
    if (layerType === "polygon") {
      const coordinates = layer.getLatLngs();
      // Use coordinates to save the field
    }
  };

  return (
    <div>
      <MapContainer center={startPosition} zoom={zoom}>
        <TileLayer
                attribution='&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                url= {tile_layer_url}
        />
        <FeatureGroup>
          <EditControl
            position="topright"
            onCreated={handleCreated}
            draw={{
              polygon: true,
              rectangle: true,
              polyline: false,
              circle: false,
              circlemarker: false,
              marker: false,
            }}
          />
        </FeatureGroup>
      </MapContainer>
    </div>
  );
};

export default MapView;
