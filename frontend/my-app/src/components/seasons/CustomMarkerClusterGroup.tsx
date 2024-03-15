import React from "react";
import L from "leaflet";
import "leaflet.markercluster";
import { useEffect } from "react";
import { useMap, Marker, Tooltip, Popup } from "react-leaflet";
import "leaflet.markercluster/dist/leaflet.markercluster";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import "../style/ClusterIcon.css";

function isReactElement(child: React.ReactNode): child is React.ReactElement {
  return child !== null && typeof child === "object" && "type" in child;
}

function isTooltipElement(element: React.ReactElement): boolean {
  return (
    element.type === Tooltip || (element.type as any).displayName === "Tooltip"
  );
}

const CustomMarkerClusterGroup = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const map = useMap();

  useEffect(() => {
    const markerClusterGroup = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
        return L.divIcon({
          html: `<div style="background: rgba(0, 0, 0, 0.5); border-radius: 100%; padding: 5px;">
                     <span style="color: white;">${cluster.getChildCount()}</span>
                   </div>`,
          className: "my-cluster-icon",
          iconSize: L.point(40, 40),
        });
      },
    });

    React.Children.forEach(children, (child) => {
      if (isReactElement(child) && child.type === Marker) {
        const marker = L.marker(child.props.position);

        React.Children.forEach(child.props.children, (subChild) => {
          if (isReactElement(subChild)) {
            if (isTooltipElement(subChild)) {
              marker.bindTooltip(subChild.props.children, subChild.props);
            }
          }
        });

        markerClusterGroup.addLayer(marker);
      }
    });

    map.addLayer(markerClusterGroup);

    return () => {
      map.removeLayer(markerClusterGroup);
    };
  }, [children, map]);

  return null;
};

export default CustomMarkerClusterGroup;
