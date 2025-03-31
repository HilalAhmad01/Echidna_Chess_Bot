import streamlit as st
import chess
import chess.svg
import chess_engine as ce
import base64

def get_svg(board, flipped=False):
    # Use standard chess.svg.board parameters without coordinates_handling
    return chess.svg.board(
        board=board,
        flipped=flipped,
        coordinates=True,  # This enables coordinates
        size=400
    )

def display_board(board, human_color):
    flipped = human_color == chess.BLACK
    svg = get_svg(board, flipped=flipped)
    
    # Convert SVG to base64
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    html = f'''
    <div style="text-align: center;">
        <img src="data:image/svg+xml;base64,{b64}" style="margin: 20px 0;"/>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def main():
    st.title("♟️ Echidna Chess Bot")
    st.markdown("---")
    
    # Initialize game state
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
        st.session_state.human_color = chess.WHITE
        st.session_state.engine_depth = 2
    
    # Game settings sidebar
    with st.sidebar:
        st.header("Game Settings")
        color_choice = st.selectbox("Play as", ["White", "Black"], index=0)
        st.session_state.human_color = chess.WHITE if color_choice == "White" else chess.BLACK
        st.session_state.engine_depth = st.slider("Engine Depth", 1, 4, 2)
        
        if st.button("New Game"):
            st.session_state.board.reset()
            st.rerun()
    
    # Display the board with coordinates
    display_board(st.session_state.board, st.session_state.human_color)
    
    # Show legal moves to help player
    if st.session_state.board.turn == st.session_state.human_color:
        st.write("Legal moves:", ", ".join([st.session_state.board.san(move) for move in st.session_state.board.legal_moves]))
    
    # Game status
    if st.session_state.board.is_checkmate():
        st.error("Checkmate! Game Over")
    elif st.session_state.board.is_game_over():
        st.warning(f"Game Over - {st.session_state.board.result()}")
    
    # Game loop
    if not st.session_state.board.is_game_over():
        if st.session_state.board.turn == st.session_state.human_color:
            # Human move
            with st.form("move_form"):
                move_input = st.text_input(
                    "Enter your move (SAN format):",
                    help="e.g. 'e4', 'Nf3', 'O-O'. See legal moves above."
                )
                submitted = st.form_submit_button("Make Move")
                
                if submitted:
                    try:
                        move = st.session_state.board.parse_san(move_input)
                        if move in st.session_state.board.legal_moves:
                            st.session_state.board.push(move)
                            st.rerun()
                        else:
                            st.error("Illegal move! See legal moves above.")
                    except ValueError:
                        st.error("Invalid move format. Use standard algebraic notation.")
        else:
            # Engine move
            with st.spinner("Engine is thinking..."):
                engine = ce.Engine(
                    st.session_state.board,
                    maxDepth=st.session_state.engine_depth,
                    color=not st.session_state.human_color
                )
                best_move = engine.getBestMove()
                st.session_state.board.push(best_move)
                st.rerun()

if __name__ == "__main__":
    main()