# ============================================================
# HEADER — TITLE + WILLOW LOGO ONLY
# ============================================================

st.html(
    f"""
    <div class="book-header">

        <div class="book-header-title">
            My Book Tree
        </div>

        <div class="willow-logo">

            <svg
                viewBox="0 0 1000 360"
                xmlns="http://www.w3.org/2000/svg"
            >

                <!-- TRUNK -->
                <path
                    d="
                        M500 360
                        C488 300 485 235 495 175
                        C500 125 515 75 535 35
                    "
                    fill="none"
                    stroke="#4A3028"
                    stroke-width="28"
                    stroke-linecap="round"
                />

                <path
                    d="
                        M504 355
                        C496 295 495 235 505 178
                        C510 125 522 78 538 38
                    "
                    fill="none"
                    stroke="#765044"
                    stroke-width="7"
                    stroke-linecap="round"
                />

                <!-- MAIN BRANCHES -->
                <g
                    fill="none"
                    stroke="#54372E"
                    stroke-linecap="round"
                >

                    <path
                        d="M500 175 C420 125 340 90 250 78"
                        stroke-width="13"
                    />

                    <path
                        d="M510 165 C590 115 675 82 765 72"
                        stroke-width="13"
                    />

                    <path
                        d="M495 205 C405 170 315 155 215 160"
                        stroke-width="10"
                    />

                    <path
                        d="M515 198 C600 165 690 155 790 165"
                        stroke-width="10"
                    />

                    <path
                        d="M500 140 C445 92 410 52 390 18"
                        stroke-width="8"
                    />

                    <path
                        d="M530 132 C585 82 620 45 640 12"
                        stroke-width="8"
                    />

                </g>

                <!-- WEEPING BRANCHES -->
                <g
                    fill="none"
                    stroke="#657452"
                    stroke-width="4"
                    stroke-linecap="round"
                >

                    <!-- LEFT -->
                    <path d="M250 78 C235 135 245 205 265 285"/>
                    <path d="M295 82 C282 145 295 220 310 305"/>
                    <path d="M340 88 C328 150 340 225 357 315"/>
                    <path d="M385 95 C372 160 385 230 402 300"/>
                    <path d="M430 108 C418 165 430 225 445 285"/>

                    <path d="M215 160 C208 215 215 265 228 325"/>

                    <!-- RIGHT -->
                    <path d="M765 72 C780 135 770 205 750 285"/>
                    <path d="M720 80 C735 145 720 220 705 305"/>
                    <path d="M675 88 C688 150 675 225 658 315"/>
                    <path d="M630 95 C643 160 630 230 613 300"/>
                    <path d="M585 108 C598 165 585 225 570 285"/>

                    <path d="M790 165 C797 215 790 265 777 325"/>

                </g>

                <!-- LEAVES -->
                <g>

                    <!-- LEFT -->
                    <ellipse
                        cx="250" cy="115"
                        rx="7" ry="21"
                        fill="#74835D"
                        transform="rotate(-20 250 115)"
                    />

                    <ellipse
                        cx="270" cy="155"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(18 270 155)"
                    />

                    <ellipse
                        cx="290" cy="205"
                        rx="7" ry="21"
                        fill="#596846"
                        transform="rotate(-15 290 205)"
                    />

                    <ellipse
                        cx="310" cy="255"
                        rx="7" ry="23"
                        fill="#74835D"
                        transform="rotate(17 310 255)"
                    />

                    <ellipse
                        cx="335" cy="135"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(-18 335 135)"
                    />

                    <ellipse
                        cx="355" cy="195"
                        rx="7" ry="23"
                        fill="#74835D"
                        transform="rotate(16 355 195)"
                    />

                    <ellipse
                        cx="380" cy="250"
                        rx="7" ry="21"
                        fill="#596846"
                        transform="rotate(-18 380 250)"
                    />

                    <ellipse
                        cx="410" cy="175"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(20 410 175)"
                    />

                    <!-- RIGHT -->
                    <ellipse
                        cx="750" cy="112"
                        rx="7" ry="21"
                        fill="#74835D"
                        transform="rotate(20 750 112)"
                    />

                    <ellipse
                        cx="730" cy="155"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(-18 730 155)"
                    />

                    <ellipse
                        cx="710" cy="205"
                        rx="7" ry="21"
                        fill="#596846"
                        transform="rotate(15 710 205)"
                    />

                    <ellipse
                        cx="690" cy="255"
                        rx="7" ry="23"
                        fill="#74835D"
                        transform="rotate(-17 690 255)"
                    />

                    <ellipse
                        cx="665" cy="135"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(18 665 135)"
                    />

                    <ellipse
                        cx="645" cy="195"
                        rx="7" ry="23"
                        fill="#74835D"
                        transform="rotate(-16 645 195)"
                    />

                    <ellipse
                        cx="620" cy="250"
                        rx="7" ry="21"
                        fill="#596846"
                        transform="rotate(18 620 250)"
                    />

                    <ellipse
                        cx="590" cy="175"
                        rx="7" ry="22"
                        fill="#89996D"
                        transform="rotate(-20 590 175)"
                    />

                </g>

                <!-- SMALL ROSE BLOSSOMS -->
                <g fill="#B87587">

                    <circle cx="295" cy="120" r="4"/>
                    <circle cx="350" cy="170" r="4"/>
                    <circle cx="405" cy="215" r="4"/>

                    <circle cx="705" cy="120" r="4"/>
                    <circle cx="650" cy="170" r="4"/>
                    <circle cx="595" cy="215" r="4"/>

                </g>

            </svg>

        </div>

    </div>
    """
)
