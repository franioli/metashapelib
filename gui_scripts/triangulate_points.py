# This script imports GCPs from a CSV file into a Metashape project.
# The CSV file should have the following format:
# image_name, gcp_name, image_u, image_v
# IMG_0001,point 1,100,200
# IMG_0001,point 2,345,400
# IMG_0002,point 2,786,211
# Note that the image_name must be equal to the image label in Metashape, so it should not have the file extension.

import os

import Metashape


def getMarker(chunk, label):
    for marker in chunk.markers:
        if marker.label == label:
            return marker
    return None


def getCamera(chunk, label):
    for camera in chunk.cameras:
        if camera.label == label:
            return camera
    return None


def main():
    path = Metashape.app.getOpenFileName("Select file with image coordinates:")

    chunk = Metashape.app.document.chunk

    with open(path, "rt") as input:
        content = input.readlines()

    # Iterate through each line in the CSV file and add the marker projections to the corresponding cameras
    for line in content:
        c_label, m_label, x_proj, y_proj = line.split(",")

        camera = getCamera(chunk, c_label)
        if not camera:
            print(f"{c_label} camera not found in project")
            continue

        marker = getMarker(chunk, m_label)
        if not marker:
            marker = chunk.addMarker()
            marker.label = m_label

        marker.projections[camera] = Metashape.Marker.Projection(
            Metashape.Vector([float(x_proj), float(y_proj)]), True
        )
        print(f"Added projection for {m_label} on {c_label}")

    # Call Metashape UpateTransform() to update the transformation matrix of the chunk
    chunk.updateTransform()

    # Export the triangulated 3D coordinates ("estimated") of the markers
    out_dir = os.path.dirname(path)
    with open(os.path.join(out_dir, "triangulated.csv"), "wt") as output:
        for marker in chunk.markers:
            coord = chunk.transform.matrix.mulp(marker.position)
            output.write(f"{marker.label},{coord.x:.6f},{coord.y:.6f},{coord.z:.6f}\n")
    print("Triangulated coordinates exported to triangulated.csv")


Metashape.app.addMenuItem("Scripts/Triangulate points", main)
