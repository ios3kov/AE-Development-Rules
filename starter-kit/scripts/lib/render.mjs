export function compare(reference, actual, tolerance) {
  if (!Number.isFinite(tolerance) || tolerance < 0) throw new Error('explicit finite nonnegative tolerance required');
  for (const image of [reference, actual]) {
    const keys = ['width','height','channels','color_space','alpha','bit_depth','pixels'];
    if (Object.keys(image).some(k => !keys.includes(k)) || keys.some(k => !(k in image))) throw new Error('invalid image fields');
    if (!Number.isInteger(image.width) || !Number.isInteger(image.height) || image.width < 1 || image.height < 1 || image.width * image.height > 1048576 || image.channels !== 4 || ![8,16,32].includes(image.bit_depth) || !['straight','premultiplied'].includes(image.alpha) || typeof image.color_space !== 'string' || !image.color_space) throw new Error('invalid render metadata');
    if (!Array.isArray(image.pixels) || image.pixels.length !== image.width*image.height*4 || image.pixels.some(v => typeof v !== 'number' || !Number.isFinite(v))) throw new Error('invalid pixels');
  }
  for (const key of ['width','height','channels','color_space','alpha','bit_depth']) if (reference[key] !== actual[key]) throw new Error('render context mismatch: ' + key);
  let maximum = 0, squared = 0, failures = 0;
  const byChannel = [0,0,0,0];
  const differences = reference.pixels.map((v,i) => {
    const d = Math.abs(v-actual.pixels[i]);
    maximum = Math.max(maximum,d); squared += d*d; byChannel[i%4] = Math.max(byChannel[i%4],d);
    if (d > tolerance) failures++;
    return d;
  });
  return { status:failures ? 'FAIL':'PASS', max_absolute_error:maximum, rmse:Math.sqrt(squared/differences.length), channel_max:byChannel, failed_samples:failures, tolerance, differences };
}
export function fixtures() {
  const image = fn => ({width:4,height:4,channels:4,color_space:'linear-sRGB',alpha:'straight',bit_depth:32,pixels:Array.from({length:16},(_,i)=>fn(i%4,Math.floor(i/4))).flat()});
  return {
    transparent:image((x,y)=>[x/3,y/3,0.5,0]),
    gradient:image((x,y)=>[x/3,y/3,(x+y)/6,0.5]),
    'float-range':image((x,y)=>[x-1,y*2,0.000001,1]),
    'edge-roi':image((x,y)=>[x===0 || x===3 ? 1:0,y===0 || y===3 ? 1:0,0,1])
  };
}
