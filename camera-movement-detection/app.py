import streamlit as st
import cv2
import numpy as np
from movement_detector import detect_camera_movement
import tempfile
import os

st.set_page_config(page_title="Camera Movement Detection", layout="wide")

st.title("📹 Camera Movement Detection System")
st.markdown("This application detects significant camera movements in video or image sequences.")

# Sidebar for parameters
st.sidebar.header("⚙️ Parameters")
diff_threshold = st.sidebar.slider("Difference Threshold", 10, 100, 30, help="Threshold value for frame difference")
match_threshold = st.sidebar.slider("Match Threshold", 0.1, 1.0, 0.7, 0.1, help="Threshold value for feature matching")
min_matches = st.sidebar.slider("Minimum Matches", 5, 50, 10, help="Minimum number of matches for homography")

# Main content
uploaded_file = st.file_uploader("Upload video or image file", type=['mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        frames = []
        
        # Check if it's a video file
        if uploaded_file.name.lower().endswith(('.mp4', '.avi', '.mov')):
            st.info("Video file uploaded. Extracting frames...")
            cap = cv2.VideoCapture(tmp_path)
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
                frame_count += 1
            cap.release()
            st.success(f"{len(frames)} frames extracted successfully.")
        else:
            # Single image
            frame = cv2.imread(tmp_path)
            if frame is not None:
                frames = [frame]
                st.success("Image uploaded successfully.")
            else:
                st.error("Failed to load image.")

        if len(frames) > 0:
            # Display first frame
            st.subheader("📸 First Frame Preview")
            first_frame_rgb = cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB)
            st.image(first_frame_rgb, caption="First frame", use_column_width=True)

            # Run detection
            if st.button("🔍 Start Movement Detection"):
                with st.spinner("Analyzing movement..."):
                    movement_indices = detect_camera_movement(
                        frames, 
                        diff_threshold=diff_threshold,
                        match_threshold=match_threshold,
                        min_matches=min_matches
                    )

                # Display results
                st.subheader("📊 Results")
                
                if movement_indices:
                    st.warning(f"🎯 {len(movement_indices)} movements detected!")
                    st.write("Frames with detected movement:", movement_indices)
                    
                    # Show movement frames
                    st.subheader("🎬 Frames with Detected Movement")
                    cols = st.columns(3)
                    for i, frame_idx in enumerate(movement_indices[:9]):  # Show first 9
                        col_idx = i % 3
                        frame_rgb = cv2.cvtColor(frames[frame_idx], cv2.COLOR_BGR2RGB)
                        with cols[col_idx]:
                            st.image(frame_rgb, caption=f"Frame {frame_idx}", use_column_width=True)
                    
                    if len(movement_indices) > 9:
                        st.info(f"... and {len(movement_indices) - 9} more frames")
                else:
                    st.success("✅ No significant camera movement detected.")

                # Show statistics
                st.subheader("📈 Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Frames", len(frames))
                with col2:
                    st.metric("Movement Detected", len(movement_indices))
                with col3:
                    if len(frames) > 0:
                        percentage = (len(movement_indices) / len(frames)) * 100
                        st.metric("Movement Rate", f"{percentage:.1f}%")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

else:
    st.info("👆 Please upload a video or image file.")
    st.markdown("""
    **Supported formats:**
    - Video: MP4, AVI, MOV
    - Image: JPG, JPEG, PNG
    """)

# Footer
st.markdown("---")
st.markdown("**Camera Movement Detection System** - Developed with OpenCV and Streamlit") 