# Utilities to Re-Use PDF files generated by FPDF for Python
# (Probably, more memory-wasting than it should)
import re, zlib

def UpdateStreamLengths(pdf):
	"Updates the streams /Length in a modified, uncompressed PDF file"
	L, Lengths=[],{}
	for m in re.finditer('<</Length (\d+)(>>)\nstream\n(.+?)\nendstream',pdf,re.S):
		oldlen, newlen = m.group(1), len(m.group(3))
		if newlen!=oldlen:
			L+=[m.start(1)]
			# length_start=old_len, next_content
			Lengths[str(m.start(1))]=(str(newlen), m.start(2))
	if not L:
		return pdf
	newpdf=''
	i=0
	for j in L:
		newpdf+=pdf[i:j]
		i=Lengths[str(j)][1]
		newpdf+=Lengths[str(j)][0]
	newpdf+=pdf[i:]
	return newpdf

def FindXRefs(pdf):
	"Returns a dictionary of {PDF object:position} found"
	XRefs={}
	for m in re.finditer('^(\d+) 0 obj',pdf,re.M):
		XRefs[int(m.group(1))] = m.start()
	return XRefs

def BuildXRefsTable(XRefs):
	"Constructs the PDF xref table from a dictionary returned by FindXRefs"
	s='xref\n'
	s+='0 '+str(len(XRefs)+1)+'\n'
	s+='0000000000 65535 f \n'
	for i in xrange(1,len(XRefs)+1):
		s+='%010d 00000 n \n'%XRefs[i]
	return s

def ReplaceXRefsTable(pdf, newtable):
	"Replaces the unique XRef table in a PDF file with the updated one"
	startxref=pdf.find('xref')
	newbuf=pdf[:startxref] + newtable + re.sub('\d+(?=\n%%EOF)',str(startxref), pdf[pdf.find('trailer'):])
	return newbuf

def DecompressStreams(pdf):
	"Decompresses all deflated streams and returns the updated PDF file"
	L, streams=[], {}
	for m in re.finditer('^<</Filter /FlateDecode /Length (\d+)>>\n(stream)',pdf,re.M):
		start=m.start(2)+7
		# stream_start: filter_start, stream_end
		streams[start]=(m.start(), start+int(m.group(1)))
		L+=[start]
	delta=0
	for i in L:
		start=i+delta
		end=streams[i][1]+delta
		stream=zlib.decompress(pdf[start:end])
		before=len(pdf)
		pdf=pdf.replace(pdf[streams[i][0]+delta:end], '<</Length %d>>\nstream\n'%len(stream)+stream)
		delta+=len(pdf)-before
	return pdf

def CompressStreams(pdf):
	"Compresses all plain streams and returns the updated PDF file"
	L, streams=[], {}
	for m in re.finditer('^<</Length (\d+)>>\n(stream)',pdf,re.M):
		start=m.start(2)+7
		# stream_start: filter_start, stream_end
		streams[start]=(m.start(), start+int(m.group(1)))
		L+=[start]
	delta=0
	for i in L:
		start=i+delta
		end=streams[i][1]+delta
		stream=zlib.compress(pdf[start:end])
		before=len(pdf)
		pdf=pdf.replace(pdf[streams[i][0]+delta:end], '<</Filter /FlateDecode /Length %d>>\nstream\n'%len(stream)+stream)
		delta+=len(pdf)-before
	return pdf

if __name__=='__main__':
	buf=file('b.pdf','rb').read()
	newbuf=DecompressStreams(buf)
	newbuf=ReplaceXRefsTable(newbuf, BuildXRefsTable(FindXRefs(newbuf)))

	newbuf=UpdateStreamLengths(newbuf) # does nothing here: test purpose only!
	file('b0.pdf','wb').write(newbuf)

	newbuf=CompressStreams(newbuf)
	newbuf=ReplaceXRefsTable(newbuf, BuildXRefsTable(FindXRefs(newbuf)))

	file('b1.pdf','wb').write(newbuf) #should be identical
