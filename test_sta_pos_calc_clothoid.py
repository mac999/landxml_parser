# title: civil information model clothoid test
# author: kang taewook
# email: laputa99999@gmail.com
# description: test clothoid (Spiral) support of civil_geo_engine using landxml_road_cl_sample.xml
#              alignment is line(300) - clothoid(80, R=400) - arc(200, R=400) - clothoid(80) - line(300)
#
import os, sys, math
import landxml_parser as lxml, civil_geo_engine as cge
from civil_geo_engine import civil_model

_test_count = 0
_fail_count = 0

def check(name, condition, detail=""):
	global _test_count, _fail_count
	_test_count += 1
	if condition:
		print(f"PASS: {name} {detail}")
	else:
		_fail_count += 1
		print(f"FAIL: {name} {detail}")

def wrap_angle(a):	# wrap to [-pi, pi)
	return (a + math.pi) % (2.0 * math.pi) - math.pi

def get_heading(align, sta, ds=0.01):
	x1, y1 = align.get_station_position(sta)
	x2, y2 = align.get_station_position(sta + ds)
	return math.atan2(y2 - y1, x2 - x1)

def get_curvature(align, sta, h=1.0):
	a1 = get_heading(align, sta - h)
	a2 = get_heading(align, sta + h)
	return wrap_angle(a2 - a1) / (2.0 * h)

def test_segment_types(align):
	types = [seg._type for seg in align._align_segments]
	check("segment types", types == ["Line", "Spiral", "Curve", "Spiral", "Line"], str(types))

def test_total_length(align):
	length = align.get_length()
	check("total length 960", abs(length - 960.0) < 0.001, f"length={length:.6f}")

def test_segment_end_positions(align):
	# engine station positions must land on the parsed segment end points
	cum_sta = 0.0
	for index, seg in enumerate(align._align_segments):
		cum_sta += seg._length
		end_point = seg._points[-1] if seg._type != "Curve" else seg._points[2]	# Curve points: Start, Center, End, PI
		x, y = align.get_station_position(min(cum_sta, align.get_length() - 0.000001))
		dist = math.dist((x, y), tuple(end_point))
		check(f"segment[{index}] {seg._type} end position", dist < 0.001, f"dist={dist:.6f} at sta={cum_sta}")

def test_tangent_continuity(align):
	# heading must be continuous across every segment boundary (G1 continuity)
	boundaries = [300.0, 380.0, 580.0, 660.0]
	for sta in boundaries:
		a1 = get_heading(align, sta - 0.1)
		a2 = get_heading(align, sta + 0.1)
		diff = abs(wrap_angle(a2 - a1))
		check(f"tangent continuity at sta {sta}", diff < 0.002, f"diff={diff:.6f} rad")

def test_curvature_profile(align):
	# clothoid: curvature must vary linearly 0 -> 1/R -> constant -> 1/R -> 0
	R = 400.0
	cases = [
		("line1 mid",         150.0, 0.0),
		("entry spiral 1/4",  320.0, -0.25 / R),
		("entry spiral mid",  340.0, -0.5 / R),
		("entry spiral 3/4",  360.0, -0.75 / R),
		("arc mid",           480.0, -1.0 / R),
		("exit spiral mid",   620.0, -0.5 / R),
		("line2 mid",         810.0, 0.0),
	]
	for name, sta, expected in cases:
		k = get_curvature(align, sta)
		check(f"curvature {name}", abs(k - expected) < 0.0001, f"k={k:.7f} expected={expected:.7f}")

def test_perp_offset(align):
	# place a point 5m on the left side (get_perpendicular_point positive offset) and project it back.
	# engine convention: get_perp_points offset is positive on the right side, so -5 is expected.
	offset = 5.0
	cases = [("line", 150.0), ("spiral", 340.0), ("arc", 480.0)]
	for name, sta in cases:
		point = align.get_perpendicular_point(sta, offset)
		results = align.get_perp_points(point, 10.0)
		matched = [r for r in results if abs(r[0] - sta) < 0.05] if results else []
		check(f"perp station on {name}", len(matched) == 1, f"stations={[round(r[0], 4) for r in (results or [])]}")
		if len(matched) == 1:
			check(f"perp offset on {name}", abs(matched[0][3] - (-offset)) < 0.01, f"offset={matched[0][3]:.6f}")

def test_polyline_plot(align, show=False):
	if show == False:
		return
	import matplotlib.pyplot as plt
	_, ax = plt.subplots()
	plt.xlabel('X Coordinate')
	plt.ylabel('Y Coordinate')
	sta_list, points = align.get_polyline(10)
	x = [position[0] for position in points]
	y = [position[1] for position in points]
	ax.scatter(x, y, c='r', s=2)
	ax.plot(x, y, c='b', linestyle='-', linewidth=1)
	ax.set_aspect('equal', 'box')
	plt.show()

def main():
	lp = lxml.landxml()
	model = lp.load('./landxml_road_cl_sample.xml')
	check("landxml load", model != None)

	cm = civil_model(model)
	check("civil model initialize", cm.initialize())

	align = cm.get_alignment(0)
	check("alignment exists", align != None)
	if align == None:
		return 1

	test_segment_types(align)
	test_total_length(align)
	test_segment_end_positions(align)
	test_tangent_continuity(align)
	test_curvature_profile(align)
	test_perp_offset(align)
	test_polyline_plot(align, show='--plot' in sys.argv)

	print(f"\n{_test_count - _fail_count}/{_test_count} tests passed")
	return 1 if _fail_count else 0

if __name__ == "__main__":
	sys.exit(main())
